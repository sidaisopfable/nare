#!/usr/bin/env python3
"""
Sage Evaluation Script
Run synthetic test entries through different configurations and compare results.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime
from test_entries import TEST_ENTRIES, get_entries_by_difficulty

# Results directory
RESULTS_DIR = Path.home() / ".sage_evals"
RESULTS_DIR.mkdir(exist_ok=True)


def extract_patterns_from_response(response: str) -> list:
    """Extract detected patterns from LLM response."""
    patterns = []
    
    # Look for pattern mentions
    pattern_map = {
        "parrot": ["parrot", "inner critic"],
        "peacock": ["peacock", "insecure performer"],
        "octopus": ["octopus", "anxious controller"],
        "golden_retriever": ["golden retriever", "compulsive pleaser"],
        "rabbit": ["rabbit", "restless escapist"]
    }
    
    response_lower = response.lower()
    for pattern, keywords in pattern_map.items():
        for keyword in keywords:
            if keyword in response_lower:
                if pattern not in patterns:
                    patterns.append(pattern)
                break
    
    return patterns


def calculate_pattern_metrics(expected: list, detected: list) -> dict:
    """Calculate precision, recall, F1 for pattern detection."""
    if not expected and not detected:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "exact_match": True}
    
    if not expected:
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0, "exact_match": len(detected) == 0}
    
    if not detected:
        return {"precision": 1.0, "recall": 0.0, "f1": 0.0, "exact_match": len(expected) == 0}
    
    true_positives = len(set(expected) & set(detected))
    precision = true_positives / len(detected) if detected else 0
    recall = true_positives / len(expected) if expected else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    exact_match = set(expected) == set(detected)
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact_match
    }


def run_single_test(entry_key: str, entry: dict, use_rag: bool, use_ollama: bool, 
                    api_key: str = None, ollama_model: str = "llama3.1:8b") -> dict:
    """Run a single test and return results."""
    
    # Import here to avoid loading heavy deps at module level
    if use_ollama:
        from app import call_ollama
        response, stats = call_ollama(
            model=ollama_model,
            context=entry["context"],
            user_input=entry["entry"],
            use_rag=use_rag
        )
    else:
        from app import call_anthropic
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("No API key provided")
        
        response, stats = call_anthropic(
            api_key=api_key,
            context=entry["context"],
            user_input=entry["entry"],
            use_rag=use_rag
        )
    
    # Extract detected patterns
    detected = extract_patterns_from_response(response)
    expected = entry.get("expected_patterns", [])
    
    # Calculate metrics
    metrics = calculate_pattern_metrics(expected, detected)
    
    return {
        "entry_key": entry_key,
        "context": entry["context"],
        "difficulty": entry.get("difficulty", "unknown"),
        "expected_patterns": expected,
        "detected_patterns": detected,
        "metrics": metrics,
        "stats": stats,
        "response": response,
        "config": {
            "use_rag": use_rag,
            "use_ollama": use_ollama,
            "model": ollama_model if use_ollama else "claude-sonnet-4"
        }
    }


def run_eval_suite(
    entries: dict = None,
    configurations: list = None,
    api_key: str = None,
    ollama_model: str = "llama3.1:8b",
    save_results: bool = True
) -> dict:
    """
    Run evaluation suite across multiple entries and configurations.
    
    Args:
        entries: Dict of entries to test (defaults to all TEST_ENTRIES)
        configurations: List of config dicts with use_rag, use_ollama keys
        api_key: Anthropic API key (required for Claude tests)
        ollama_model: Which Ollama model to use
        save_results: Whether to save results to file
    
    Returns:
        Aggregated results dict
    """
    if entries is None:
        entries = TEST_ENTRIES
    
    if configurations is None:
        configurations = [
            {"use_rag": True, "use_ollama": False, "name": "Claude + RAG"},
            {"use_rag": False, "use_ollama": False, "name": "Claude (no RAG)"},
        ]
        # Only add Ollama configs if available
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                configurations.extend([
                    {"use_rag": True, "use_ollama": True, "name": "Ollama + RAG"},
                    {"use_rag": False, "use_ollama": True, "name": "Ollama (no RAG)"},
                ])
        except:
            print("⚠️  Ollama not available, skipping Ollama tests")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "configurations": {},
        "summary": {}
    }
    
    for config in configurations:
        config_name = config.get("name", f"rag={config['use_rag']}_ollama={config['use_ollama']}")
        print(f"\n{'='*60}")
        print(f"Running: {config_name}")
        print(f"{'='*60}")
        
        config_results = []
        total_time = 0
        total_cost = 0
        
        for entry_key, entry in entries.items():
            print(f"  Testing: {entry_key}...", end=" ", flush=True)
            
            try:
                result = run_single_test(
                    entry_key=entry_key,
                    entry=entry,
                    use_rag=config["use_rag"],
                    use_ollama=config["use_ollama"],
                    api_key=api_key,
                    ollama_model=ollama_model
                )
                config_results.append(result)
                total_time += result["stats"].get("time", 0)
                total_cost += result["stats"].get("cost", 0)
                
                # Show quick result
                if result["metrics"]["exact_match"]:
                    print("✅ exact match")
                else:
                    print(f"⚠️  expected {result['expected_patterns']}, got {result['detected_patterns']}")
                    
            except Exception as e:
                print(f"❌ error: {e}")
                config_results.append({
                    "entry_key": entry_key,
                    "error": str(e)
                })
        
        # Calculate aggregate metrics
        successful = [r for r in config_results if "metrics" in r]
        if successful:
            avg_precision = sum(r["metrics"]["precision"] for r in successful) / len(successful)
            avg_recall = sum(r["metrics"]["recall"] for r in successful) / len(successful)
            avg_f1 = sum(r["metrics"]["f1"] for r in successful) / len(successful)
            exact_matches = sum(1 for r in successful if r["metrics"]["exact_match"])
            
            results["configurations"][config_name] = {
                "results": config_results,
                "aggregate": {
                    "total_entries": len(entries),
                    "successful": len(successful),
                    "exact_matches": exact_matches,
                    "exact_match_rate": exact_matches / len(successful) if successful else 0,
                    "avg_precision": avg_precision,
                    "avg_recall": avg_recall,
                    "avg_f1": avg_f1,
                    "total_time": total_time,
                    "avg_time": total_time / len(successful) if successful else 0,
                    "total_cost": total_cost
                }
            }
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for config_name, data in results["configurations"].items():
        agg = data["aggregate"]
        print(f"\n{config_name}:")
        print(f"  Exact match rate: {agg['exact_match_rate']*100:.1f}% ({agg['exact_matches']}/{agg['successful']})")
        print(f"  Avg F1: {agg['avg_f1']:.3f}")
        print(f"  Avg time: {agg['avg_time']:.2f}s")
        print(f"  Total cost: ${agg['total_cost']:.4f}")
    
    # Save results
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = RESULTS_DIR / f"eval_{timestamp}.json"
        
        # Remove full responses for file size
        results_for_save = json.loads(json.dumps(results))
        for config_data in results_for_save["configurations"].values():
            for r in config_data.get("results", []):
                if "response" in r:
                    r["response"] = r["response"][:500] + "..." if len(r.get("response", "")) > 500 else r.get("response", "")
        
        filepath.write_text(json.dumps(results_for_save, indent=2))
        print(f"\n📁 Results saved to: {filepath}")
    
    return results


def quick_test(api_key: str = None):
    """Run a quick test with just a few entries."""
    quick_entries = {
        k: v for k, v in TEST_ENTRIES.items() 
        if v.get("difficulty") == "obvious"
    }
    return run_eval_suite(
        entries=dict(list(quick_entries.items())[:3]),
        api_key=api_key
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Sage evaluation suite")
    parser.add_argument("--quick", action="store_true", help="Run quick test (3 entries)")
    parser.add_argument("--difficulty", choices=["obvious", "subtle", "complex", "edge"], 
                        help="Only test entries of this difficulty")
    parser.add_argument("--api-key", help="Anthropic API key")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    
    if args.quick:
        quick_test(api_key)
    elif args.difficulty:
        entries = dict(get_entries_by_difficulty(args.difficulty))
        run_eval_suite(entries=entries, api_key=api_key)
    else:
        run_eval_suite(api_key=api_key)
