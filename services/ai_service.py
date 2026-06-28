"""
AI Service - AI-powered summarization, decision extraction, action item suggestion,
grammar cleanup, and quality checking.
Uses OpenAI API (GPT) for all text processing.
"""

import os
import json
from models.activity_log import ActivityLogModel


class AIService:
    """Service for AI-powered text processing using OpenAI."""

    @staticmethod
    def _get_client():
        """Get an OpenAI client. Raises if no API key is set."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please add it to your .env file."
            )
        from openai import OpenAI
        return OpenAI(api_key=api_key)

    @staticmethod
    def _chat(prompt: str, system: str = "", temperature: float = 0.3,
              max_tokens: int = 1500) -> str:
        """Send a chat completion request and return the text response."""
        client = AIService._get_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    # ==================================================================
    # F16 — AI Summary Generator
    # ==================================================================

    @staticmethod
    def summarize_text(text: str, user_id=None) -> dict:
        """
        Summarize meeting discussion text.
        Returns dict with 'success', 'summary', 'decisions', 'action_items', 'message'.
        """
        if not text or not text.strip():
            return {
                "success": False, "summary": "", "decisions": "",
                "action_items": [], "message": "No text provided.",
            }

        try:
            return AIService._summarize_with_openai(text, user_id)
        except Exception as e:
            return {
                "success": False, "summary": "", "decisions": "",
                "action_items": [], "message": f"AI error: {str(e)}",
            }

    @staticmethod
    def _summarize_with_openai(text: str, user_id=None) -> dict:
        """Use OpenAI API for summarization."""
        try:
            system = (
                "You are a professional meeting assistant. You analyze meeting "
                "notes and produce structured summaries."
            )

            prompt = f"""Analyze the following meeting notes and provide:

1. **Summary**: A concise summary of the discussion (2-4 sentences).
2. **Key Decisions**: A bullet list of decisions made.
3. **Action Items**: A list of action items with the format: "- [Task] → Assigned to: [Person] | Deadline: [Date if mentioned]"

Meeting Notes:
---
{text}
---

Respond in plain text with clear section headers: SUMMARY, DECISIONS, ACTION ITEMS."""

            result_text = AIService._chat(prompt, system=system)
            parsed = AIService._parse_ai_response(result_text)

            if user_id:
                ActivityLogModel.log_activity(
                    user_id=user_id, username="",
                    action="AI Summary Generated",
                    details="Generated summary using OpenAI API",
                )

            return {
                "success": True,
                "summary": parsed["summary"],
                "decisions": parsed["decisions"],
                "action_items": parsed["action_items"],
                "message": "AI summary generated using OpenAI.",
            }

        except Exception as e:
            return {
                "success": False, "summary": "", "decisions": "",
                "action_items": [], "message": f"OpenAI error: {str(e)}",
            }

    @staticmethod
    def clean_grammar(text: str, user_id=None) -> dict:
        """
        Clean grammar and improve sentence structure in rough notes.
        Returns dict with 'success', 'cleaned_text', 'message'.
        """
        if not text or not text.strip():
            return {"success": False, "cleaned_text": "", "message": "No text provided."}

        try:
            system = (
                "You are a professional editor. Fix grammar, spelling, and "
                "improve sentence structure while keeping the original meaning. "
                "Do NOT add new content — only clean up what is given."
            )
            prompt = f"""Clean up the following rough meeting notes. Fix grammar, spelling, and improve sentence structure. Keep all the original content and meaning intact.

Rough Notes:
---
{text}
---

Return only the cleaned-up text, nothing else."""

            cleaned = AIService._chat(prompt, system=system, temperature=0.2)

            if user_id:
                ActivityLogModel.log_activity(
                    user_id=user_id, username="",
                    action="AI Grammar Cleanup",
                    details="Cleaned grammar using OpenAI API",
                )

            return {"success": True, "cleaned_text": cleaned, "message": "Text cleaned successfully."}

        except Exception as e:
            return {"success": False, "cleaned_text": "", "message": f"AI error: {str(e)}"}

    @staticmethod
    def format_rough_notes_to_mom(text: str, user_id=None) -> dict:
        """
        Convert rough handwritten or voice notes into a formatted MoM structure.
        Returns dict with 'success', 'agenda', 'discussion', 'decisions', 'action_items', 'message'.
        """
        if not text or not text.strip():
            return {
                "success": False, "agenda": "", "discussion": "",
                "decisions": "", "action_items": [],
                "message": "No text provided.",
            }

        try:
            system = (
                "You are a meeting minutes formatter. Convert rough, unstructured "
                "notes into a properly structured Minutes of Meeting format."
            )

            prompt = f"""Convert the following rough notes into a structured Minutes of Meeting format. Extract and organize them into these sections:

1. AGENDA — A numbered list of topics discussed
2. DISCUSSION — A clean, well-written summary of what was discussed
3. DECISIONS — A bullet list of decisions that were made
4. ACTION ITEMS — Each in format: "- [Task description] → Assigned to: [Person] | Deadline: [Date if mentioned]"

Rough Notes:
---
{text}
---

Respond with clear section headers: AGENDA, DISCUSSION, DECISIONS, ACTION ITEMS."""

            result_text = AIService._chat(prompt, system=system, max_tokens=2000)
            parsed = AIService._parse_full_mom_response(result_text)

            if user_id:
                ActivityLogModel.log_activity(
                    user_id=user_id, username="",
                    action="AI Notes Formatted",
                    details="Formatted rough notes into MoM structure using OpenAI",
                )

            return {
                "success": True,
                "agenda": parsed["agenda"],
                "discussion": parsed["discussion"],
                "decisions": parsed["decisions"],
                "action_items": parsed["action_items"],
                "message": "Rough notes formatted into MoM structure.",
            }

        except Exception as e:
            return {
                "success": False, "agenda": "", "discussion": "",
                "decisions": "", "action_items": [],
                "message": f"AI error: {str(e)}",
            }

    # ==================================================================
    # F18 — Live Meeting Recording Summarizer
    # ==================================================================

    @staticmethod
    def summarize_live_recording(transcript: str, user_id=None) -> dict:
        """
        Summarize a full live meeting recording transcript into a complete MoM.
        Extracts: title, agenda, discussion, decisions, action items (with
        assigned person + deadline), and overall meeting outcome/result.
        Returns dict with 'success', 'title', 'agenda', 'discussion',
        'decisions', 'action_items', 'outcome', 'message'.
        Each action_item: {'description': str, 'assigned_to': str, 'deadline': str}
        """
        if not transcript or not transcript.strip():
            return {
                "success": False, "title": "", "agenda": "",
                "discussion": "", "decisions": "",
                "action_items": [], "outcome": "",
                "message": "No transcript provided.",
            }
        try:
            system = (
                "You are an expert meeting analyst and professional minute-taker. "
                "You analyze full meeting transcripts and produce comprehensive, "
                "well-structured Minutes of Meeting documents. "
                "Be precise about task assignments and deadlines mentioned."
            )

            prompt = f"""Analyze the following complete meeting transcript and extract ALL key information.

Provide the output in EXACTLY this structure with these section headers:

MEETING TITLE
[Generate a clear, professional title that describes what this meeting was about]

AGENDA
[A numbered list of the main topics discussed, one per line]

DISCUSSION
[A comprehensive summary of everything discussed. Include key points, debates, and context. Write in professional meeting minutes style.]

DECISIONS
[A bullet list (using -) of every decision that was made. Each decision on its own line.]

ACTION ITEMS
[Each action item on its own line in EXACTLY this format:]
- [Task description] | Assigned to: [Person's name or 'TBD'] | Deadline: [Date or 'TBD']

OUTCOME
[A 2-3 sentence summary of the overall meeting result, what was achieved, and what the next steps are.]

Meeting Transcript:
---
{transcript}
---

IMPORTANT:
- Extract REAL names mentioned in the transcript for action item assignments.
- If deadlines are mentioned (e.g. "by Friday", "next week", "end of month"), include them.
- If no deadline is mentioned, write 'TBD'.
- If a task has no named assignee, write 'TBD'.
- Do NOT invent information not present in the transcript."""

            result_text = AIService._chat(
                prompt, system=system,
                temperature=0.2, max_tokens=3000
            )
            parsed = AIService._parse_live_recording_response(result_text)

            if user_id:
                ActivityLogModel.log_activity(
                    user_id=user_id, username="",
                    action="Live Recording Summarized",
                    details=f"Summarized live meeting transcript ({len(transcript)} chars) using gpt-4o-mini",
                )

            return {
                "success": True,
                "title": parsed["title"],
                "agenda": parsed["agenda"],
                "discussion": parsed["discussion"],
                "decisions": parsed["decisions"],
                "action_items": parsed["action_items"],
                "outcome": parsed["outcome"],
                "message": "Live meeting summarized successfully using gpt-4o-mini.",
            }

        except Exception as e:
            return {
                "success": False, "title": "", "agenda": "",
                "discussion": "", "decisions": "",
                "action_items": [], "outcome": "",
                "message": f"AI summarization error: {str(e)}",
            }

    @staticmethod
    def _parse_live_recording_response(text: str) -> dict:
        """Parse the live recording AI response into structured MoM fields."""
        result = {
            "title": "", "agenda": "", "discussion": "",
            "decisions": "", "action_items": [], "outcome": ""
        }
        current_section = ""

        for line in text.split("\n"):
            stripped = line.strip()
            upper = stripped.upper()

            # Detect section headers
            if upper == "MEETING TITLE" or upper.startswith("MEETING TITLE"):
                current_section = "title"
                continue
            elif upper == "AGENDA" or (upper.startswith("AGENDA") and len(upper) < 20):
                current_section = "agenda"
                continue
            elif upper == "DISCUSSION" or (upper.startswith("DISCUSSION") and len(upper) < 20):
                current_section = "discussion"
                continue
            elif upper == "DECISIONS" or (upper.startswith("DECISIONS") and len(upper) < 20):
                current_section = "decisions"
                continue
            elif upper == "ACTION ITEMS" or (upper.startswith("ACTION ITEMS") and len(upper) < 25):
                current_section = "action_items"
                continue
            elif upper == "OUTCOME" or (upper.startswith("OUTCOME") and len(upper) < 20):
                current_section = "outcome"
                continue

            # Skip empty lines between sections
            if not stripped:
                if current_section not in ("discussion", "decisions"):
                    continue

            # Accumulate content
            if current_section == "title":
                if stripped and not result["title"]:
                    result["title"] = stripped.lstrip("#").strip()
            elif current_section == "agenda":
                if stripped:
                    result["agenda"] += stripped + "\n"
            elif current_section == "discussion":
                result["discussion"] += stripped + "\n"
            elif current_section == "decisions":
                result["decisions"] += stripped + "\n"
            elif current_section == "action_items":
                if stripped.startswith("-") or stripped.startswith("•") or stripped.startswith("*"):
                    raw = stripped.lstrip("-•* ").strip()
                    # Parse: "Task | Assigned to: Person | Deadline: Date"
                    ai_item = {"description": raw, "assigned_to": "TBD", "deadline": "TBD"}
                    if "|" in raw:
                        parts = [p.strip() for p in raw.split("|")]
                        ai_item["description"] = parts[0]
                        for part in parts[1:]:
                            if part.lower().startswith("assigned to:"):
                                ai_item["assigned_to"] = part.split(":", 1)[1].strip()
                            elif part.lower().startswith("deadline:"):
                                ai_item["deadline"] = part.split(":", 1)[1].strip()
                    result["action_items"].append(ai_item)
            elif current_section == "outcome":
                if stripped:
                    result["outcome"] += stripped + " "

        # Clean up
        result["agenda"] = result["agenda"].strip()
        result["discussion"] = result["discussion"].strip()
        result["decisions"] = result["decisions"].strip()
        result["outcome"] = result["outcome"].strip()
        return result

    # ==================================================================
    # F17 — AI Quality Checker
    # ==================================================================

    @staticmethod
    def quality_check(agenda: str, discussion: str, decisions: str,
                      action_items: list, user_id=None) -> dict:
        """
        Pre-save quality check on a MoM.
        Checks for completeness, missing fields, and vague statements.
        Returns dict with 'success', 'issues' (list of dicts), 'score', 'message'.
        Each issue: {'severity': 'warning'|'error'|'info', 'field': str, 'message': str}
        """
        issues = []
        # ---- Rule-based checks first (fast, no API call) ----

        # Missing fields
        if not agenda or not agenda.strip():
            issues.append({
                "severity": "warning", "field": "Agenda",
                "message": "Agenda is empty — consider adding meeting topics."
            })
        if not discussion or not discussion.strip():
            issues.append({
                "severity": "warning", "field": "Discussion",
                "message": "Discussion section is empty."
            })
        if not decisions or not decisions.strip():
            issues.append({
                "severity": "info", "field": "Decisions",
                "message": "No decisions recorded — add any decisions made."
            })

        # Action item checks
        if not action_items:
            issues.append({
                "severity": "info", "field": "Action Items",
                "message": "No action items — consider adding tasks if any were assigned."
            })
        else:
            for i, item in enumerate(action_items):
                desc = item.get("description", "").strip()
                if not desc:
                    continue
                assigned = item.get("assigned_to", "").strip()
                deadline = item.get("deadline")
                if not assigned:
                    issues.append({
                        "severity": "warning", "field": f"Action Item {i+1}",
                        "message": f'"{desc[:50]}..." has no assigned person.'
                    })
                if not deadline:
                    issues.append({
                        "severity": "warning", "field": f"Action Item {i+1}",
                        "message": f'"{desc[:50]}..." has no deadline set.'
                    })

        # ---- AI-based clarity check (if there are decisions) ----
        if decisions and decisions.strip():
            try:
                ai_issues = AIService._ai_clarity_check(decisions, discussion)
                issues.extend(ai_issues)
            except Exception:
                pass  # Don't block save if AI check fails

        # Calculate quality score
        error_count = sum(1 for i in issues if i["severity"] == "error")
        warning_count = sum(1 for i in issues if i["severity"] == "warning")
        info_count = sum(1 for i in issues if i["severity"] == "info")

        score = max(0, 100 - (error_count * 20) - (warning_count * 10) - (info_count * 3))

        if user_id:
            ActivityLogModel.log_activity(
                user_id=user_id, username="",
                action="AI Quality Check",
                details=f"Quality score: {score}/100 — {len(issues)} issue(s) found",
            )

        return {
            "success": True,
            "issues": issues,
            "score": score,
            "message": f"Quality check complete — score: {score}/100",
        }

    @staticmethod
    def _ai_clarity_check(decisions: str, discussion: str = "") -> list:
        """Use AI to check for vague decision statements."""
        try:
            system = (
                "You are a meeting quality reviewer. Your job is to flag vague, "
                "unclear, or non-actionable decision statements."
            )

            prompt = f"""Review the following decisions from a meeting. Flag any that are:
- Vague or non-committal (e.g., "we will think about it", "to be decided later", "maybe")
- Missing a clear owner or responsible person
- Too generic to be actionable

Decisions:
---
{decisions}
---

{"Discussion context: " + discussion[:500] if discussion else ""}

Respond ONLY as a JSON array of objects. Each object:
{{"severity": "warning", "field": "Decisions", "message": "your finding"}}

If no issues found, respond with an empty array: []
Return ONLY the JSON array, no other text."""

            result = AIService._chat(prompt, system=system, temperature=0.2, max_tokens=800)

            # Parse JSON response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1] if "\n" in result else result
                result = result.rsplit("```", 1)[0] if "```" in result else result
                result = result.strip()

            parsed = json.loads(result)
            if isinstance(parsed, list):
                # Validate structure
                valid_issues = []
                for item in parsed:
                    if isinstance(item, dict) and "message" in item:
                        valid_issues.append({
                            "severity": item.get("severity", "warning"),
                            "field": item.get("field", "Decisions"),
                            "message": item["message"],
                        })
                return valid_issues
            return []

        except (json.JSONDecodeError, Exception):
            return []

    # ==================================================================
    # Parsing Helpers
    # ==================================================================

    @staticmethod
    def _parse_ai_response(text: str) -> dict:
        """Parse AI response into structured sections (summary, decisions, action_items)."""
        result = {"summary": "", "decisions": "", "action_items": []}
        current_section = ""

        for line in text.split("\n"):
            line_upper = line.strip().upper()
            if "SUMMARY" in line_upper and len(line_upper) < 30:
                current_section = "summary"
                continue
            elif "DECISION" in line_upper and len(line_upper) < 30:
                current_section = "decisions"
                continue
            elif "ACTION" in line_upper and "ITEM" in line_upper and len(line_upper) < 30:
                current_section = "action_items"
                continue

            if current_section == "summary":
                result["summary"] += line.strip() + " "
            elif current_section == "decisions":
                result["decisions"] += line.strip() + "\n"
            elif current_section == "action_items":
                stripped = line.strip()
                if stripped.startswith("-") or stripped.startswith("•") or stripped.startswith("*"):
                    result["action_items"].append(stripped.lstrip("-•*").strip())

        result["summary"] = result["summary"].strip()
        result["decisions"] = result["decisions"].strip()
        return result

    @staticmethod
    def _parse_full_mom_response(text: str) -> dict:
        """Parse AI response into full MoM structure (agenda, discussion, decisions, action_items)."""
        result = {"agenda": "", "discussion": "", "decisions": "", "action_items": []}
        current_section = ""

        for line in text.split("\n"):
            line_upper = line.strip().upper()
            if "AGENDA" in line_upper and len(line_upper) < 30:
                current_section = "agenda"
                continue
            elif "DISCUSSION" in line_upper and len(line_upper) < 30:
                current_section = "discussion"
                continue
            elif "DECISION" in line_upper and len(line_upper) < 30:
                current_section = "decisions"
                continue
            elif "ACTION" in line_upper and "ITEM" in line_upper and len(line_upper) < 30:
                current_section = "action_items"
                continue

            if current_section == "agenda":
                result["agenda"] += line.strip() + "\n"
            elif current_section == "discussion":
                result["discussion"] += line.strip() + "\n"
            elif current_section == "decisions":
                result["decisions"] += line.strip() + "\n"
            elif current_section == "action_items":
                stripped = line.strip()
                if stripped.startswith("-") or stripped.startswith("•") or stripped.startswith("*"):
                    result["action_items"].append(stripped.lstrip("-•*").strip())

        result["agenda"] = result["agenda"].strip()
        result["discussion"] = result["discussion"].strip()
        result["decisions"] = result["decisions"].strip()
        return result
