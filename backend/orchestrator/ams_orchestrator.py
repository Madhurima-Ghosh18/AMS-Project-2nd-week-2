# orchestrator/ams_orchestrator.py

from modules.duplicate_detection.handler import handle_duplicate_flow
from modules.copilot_rca.handler         import handle_rca_flow


async def handle_ticket(data):

    state = {
        "data":         data,
        "summary":      getattr(data, "summary", "") if data else "",
        "type":         None,
        "id":           None,
        "message":      None,
        "is_duplicate": False,

        # rca defaults
        "rca_root_cause":       None,
        "rca_affected":         None,
        "rca_steps":            [],
        "rca_confidence":       None,
        "rca_confidence_label": None,
        "rca_summary":          None,
    }

    try:
        # ── STEP 1: DUPLICATE DETECTION ──
        state = await safe_run_module(handle_duplicate_flow, state)

        # summary safety fallback
        if not state.get("summary") and state.get("data"):
            data_obj = state["data"]
            state["summary"] = getattr(data_obj, "summary", "") \
                if hasattr(data_obj, "summary") else ""

        if state.get("is_duplicate"):
            return normalize_response(state)

        # ── STEP 2: RCA GENERATION ──
        state = await safe_run_module(handle_rca_flow, state)

        return normalize_response(state)

    except Exception as e:
        return {
            "type":    "error",
            "message": f"Orchestrator failed: {str(e)}"
        }


async def safe_run_module(module_fn, state: dict):
    try:
        result = await module_fn(state)
        if not isinstance(result, dict):
            return {
                **state,
                "type":    "error",
                "message": "Module returned invalid state"
            }
        state.update(result)
        return state
    except Exception as e:
        return {
            **state,
            "type":    "error",
            "message": f"Module failed: {str(e)}"
        }


def normalize_response(state: dict):
    return {
        "type":    state.get("type", "success"),
        "id":      state.get("id"),
        "message": state.get("message"),

        # RCA — only included if root cause was generated
        "rca": {
            "root_cause":       state.get("rca_root_cause"),
            "affected":         state.get("rca_affected"),
            "steps":            state.get("rca_steps", []),
            "confidence":       state.get("rca_confidence"),
            "confidence_label": state.get("rca_confidence_label"),
            "summary":          state.get("rca_summary"),
        } if state.get("rca_root_cause") else None,
    }