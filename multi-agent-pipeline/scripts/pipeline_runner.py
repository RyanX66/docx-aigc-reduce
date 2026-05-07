#!/usr/bin/env python3
"""
Multi-Agent Pipeline Runner
Orchestrates the 5-agent document processing pipeline:
  Agent 1: Structure Analyzer (extract body paragraphs)
  Agent 2: Content Rewriter R1 (vocabulary + redundancy)
  Agent 3: Content Rewriter R2 (AI-cliche removal)
  Agent 4: Format Writer (write back to .docx)
  Agent 5: Validator (verify integrity)

Supports checkpoint/resume via state file (pipeline_state.json).
"""
import json, sys, os, subprocess, time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Agent:
    name: str
    description: str
    script: str
    inputs: list
    outputs: list

@dataclass
class PipelineState:
    doc_id: str
    current_step: int = 0
    steps: list = field(default_factory=list)
    start_time: str = ""
    history: list = field(default_factory=list)

    @classmethod
    def load(cls, path: str):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state = cls(data["doc_id"])
                state.current_step = data["current_step"]
                state.steps = data["steps"]
                state.start_time = data["start_time"]
                state.history = data.get("history", [])
                return state
        return None

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "doc_id": self.doc_id,
                "current_step": self.current_step,
                "steps": self.steps,
                "start_time": self.start_time,
                "history": self.history,
            }, f, ensure_ascii=False, indent=2)


def create_pipeline(input_docx: str, output_docx: str) -> PipelineState:
    """Create a new pipeline for a document."""
    doc_id = os.path.basename(input_docx)
    state = PipelineState(doc_id=doc_id, start_time=datetime.now().isoformat())

    intermediate_dir = "finish/intermediate"
    state.steps = [
        {
            "id": 1,
            "agent": "Structure Analyzer",
            "status": "pending",
            "command": f"python scripts/extract_body.py {input_docx} {intermediate_dir}/body_paragraphs.json",
            "output": f"{intermediate_dir}/body_paragraphs.json",
        },
        {
            "id": 2,
            "agent": "Content Rewriter R1",
            "status": "pending",
            "command": f"python scripts/rewrite_engine.py --round 1 --input {intermediate_dir}/body_paragraphs.json --output {intermediate_dir}/rewrite_r1.json",
            "output": f"{intermediate_dir}/rewrite_r1.json",
        },
        {
            "id": 3,
            "agent": "Content Rewriter R2",
            "status": "pending",
            "command": f"python scripts/rewrite_engine.py --round 2 --input {intermediate_dir}/rewrite_r1.json --output {intermediate_dir}/rewrite_mapping.json",
            "output": f"{intermediate_dir}/rewrite_mapping.json",
        },
        {
            "id": 4,
            "agent": "Format Writer",
            "status": "pending",
            "command": f"python scripts/apply_rewrite.py {input_docx} {intermediate_dir}/rewrite_mapping.json {output_docx}",
            "output": output_docx,
        },
        {
            "id": 5,
            "agent": "Validator",
            "status": "pending",
            "command": f"python scripts/verify.py {input_docx} {output_docx}",
            "output": "verification report (stdout)",
        },
    ]

    return state


def run_pipeline(state: PipelineState):
    """Execute remaining steps in the pipeline."""
    total = len(state.steps)
    passed = 0
    failed = 0

    print("=" * 60)
    print(f"  Multi-Agent Pipeline: {state.doc_id}")
    print(f"  State: {state.start_time}")
    print("=" * 60)

    for step in state.steps:
        if step["id"] <= state.current_step:
            print(f"\n  Step {step['id']}/{total}: {step['agent']} [SKIPPED - already done]")
            continue

        print(f"\n  Step {step['id']}/{total}: {step['agent']}")
        print(f"  Running: {step['command']}")
        print(f"  " + "-" * 50)

        t0 = time.time()
        result = subprocess.run(step["command"], shell=True, capture_output=True, text=True)
        elapsed = time.time() - t0

        if result.returncode == 0:
            step["status"] = "completed"
            passed += 1
            print(f"  [OK] Completed in {elapsed:.1f}s")
        else:
            step["status"] = "failed"
            failed += 1
            print(f"  [FAIL] Error (exit code {result.returncode})")
            if result.stderr:
                print(f"  {result.stderr[:200]}")

        state.current_step = step["id"]
        state.history.append({
            "step": step["id"],
            "agent": step["agent"],
            "status": step["status"],
            "duration_s": round(elapsed, 1),
            "timestamp": datetime.now().isoformat(),
        })
        state.save("pipeline_state.json")

        if step["status"] == "failed":
            print(f"\n  Pipeline stopped at step {step['id']}. Fix the error and re-run to resume.")
            return

    print(f"\n{'=' * 60}")
    print(f"  Pipeline Complete: {passed}/{total} steps passed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pipeline_runner.py <input.docx> <output.docx> [--resume]")
        sys.exit(1)

    input_docx = sys.argv[1]
    output_docx = sys.argv[2]
    resume = "--resume" in sys.argv

    if resume:
        state = PipelineState.load("pipeline_state.json")
        if state is None:
            print("No saved state found. Starting new pipeline.")
            state = create_pipeline(input_docx, output_docx)
    else:
        # Start fresh
        if os.path.exists("pipeline_state.json"):
            os.remove("pipeline_state.json")
        state = create_pipeline(input_docx, output_docx)

    run_pipeline(state)
