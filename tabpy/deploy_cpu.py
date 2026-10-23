import os
from tabpy.tabpy_tools.client import Client


# --------------------------------------------------
# 1. Load .env from the same folder as this script
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

if os.path.isfile(ENV_FILE):
    with open(ENV_FILE, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")

            if name and name not in os.environ:
                os.environ[name] = value


# --------------------------------------------------
# 2. AI-based complete system assessment (Google Gemini)
#    Company System  -> Approved (no AI check)
#    Personal System -> Full AI check based on team work
#
#    Optional .env settings (all have defaults):
#      AI_TIME_BUDGET    seconds one Tableau call may spend on Gemini (default 25)
#      AI_READ_TIMEOUT   max seconds to wait for one Gemini reply (default 40)
#      AI_THINKING_LEVEL e.g. "low" (Gemini 3) - only sent if set
#      AI_THINKING_BUDGET e.g. "0" (Gemini 2.5) - only sent if set
#      CHECK_CACHE_FILE  path of the on-disk result cache
# --------------------------------------------------
def check_system(cpus, rams, storages, nets, sys_types, teams, system_owners):
    # Imports inside the function so TabPy serializes them reliably
    import os
    import json
    import time
    import requests

    start = time.time()

    model = os.environ["AI_MODEL"]
    api_key = os.environ["AI_API_KEY"]

    def env_float(name, default):
        try:
            return float(os.environ.get(name, default))
        except ValueError:
            return float(default)

    time_budget = env_float("AI_TIME_BUDGET", 25)
    max_read_timeout = env_float("AI_READ_TIMEOUT", 40)
    deadline = start + time_budget

    cache_file = os.environ.get(
        "CHECK_CACHE_FILE",
        os.path.join(os.path.expanduser("~"), "check_system_cache.json"),
    )

    gemini_url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + model
        + ":generateContent"
    )

    # ---------------- disk cache (successful results only) ----------------
    def load_cache():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save_cache(data):
        try:
            tmp = cache_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp, cache_file)
        except Exception as exc:
            print("CACHE WRITE ERROR:", repr(exc))

    cache = load_cache()

    system_instruction = (
        "You are a careful IT hardware assessor. "
        "Be practical, technically accurate and "
        "honest about uncertainty. Never invent "
        "hardware specifications."
    )

    # Team-wise work profile. Edit these as per your real team work.
    team_work = {
        "CSA": """
        Team CSA work:
        - Client/support analysis, reporting and data validation.
        - SQL queries on BigQuery, Excel/Sheets, dashboards.
        - Browser tabs, video meetings, office applications.
        - Light Python/VS Code usage.
        """,
        "CUBE": """
        Team Cube work:
        - Cube (semantic layer) development, Node.js and YAML/JS models.
        - BigQuery/GCP connections, API testing.
        - Docker containers for local Cube setup, VS Code, terminals.
        - Browser, Postman-type tools and video meetings.
        """,
        "DATA MART": """
        Team Data Mart work:
        - BigQuery SQL, data modeling and data mart pipelines on GCP.
        - Python, notebooks, VS Code, dbt-style transformations.
        - Validating large result sets, many browser tabs and meetings.
        """,
        "EDW": """
        Team EDW work:
        - Enterprise data warehouse design, ETL/ELT pipelines on GCP.
        - Heavy SQL, large extracts and comparisons, SQL clients.
        - Python scripts, Airflow/orchestration tools, GCP Console.
        - Heavy multitasking with many tabs and applications.
        """,
        "LLM": """
        Team LLM work:
        - AI/LLM application development, mostly via cloud APIs.
        - Python, notebooks, embeddings, vector data, Docker.
        - Occasional small local model testing.
        - A dedicated GPU is needed only if large local models are
          trained or run locally; cloud GPU/API usage does not need it.
        """,
        "LOOKER": """
        Team Looker work:
        - LookML development in browser IDE, dashboards and reporting.
        - Many browser tabs open together, Git, BigQuery, video meetings.
        - Browser heavy workload, so RAM and stable internet matter most.
        """,
        "OPS": """
        Team OPS work:
        - Cloud and pipeline monitoring, GCP Console, logs and alerts.
        - Terminals, scripts, incident handling over video calls.
        - Stable internet is critical; compute need is moderate.
        """,
        "QA": """
        Team QA work:
        - Data and application testing, test automation scripts.
        - Multiple browsers, Selenium/Playwright style tools, Docker.
        - BigQuery validation queries, Python, VS Code, meetings.
        """,
        "UI/UX": """
        Team UI/UX work:
        - Design tools such as Figma, prototyping, image/asset editing.
        - Many browser tabs, large design files, video meetings.
        - Smooth graphics, good RAM and fast SSD matter; display quality
          and integrated/dedicated GPU capability can matter more here.
        """,
    }

    generic_work = """
    Team not recognised. Assume a general data engineering and analytics
    employee (GCP, BigQuery, Looker, Python, VS Code, browser tabs, meetings).
    """

    base_requirements = """
    Assess a personal laptop that an employee wants to use for office work
    from home.

    Important workload distinction:
    Heavy data processing can run on GCP cloud infrastructure.
    Do not assume the laptop must process all cloud data locally.
    However, local development, Docker, multitasking and large local datasets
    still require adequate laptop resources.

    Assess the COMPLETE configuration together, not just one component
    against a rigid checklist. Consider CPU generation and capability,
    available RAM, storage capacity and type, internet suitability,
    and whether the configuration can realistically support the
    team's work described above.

    Do not automatically reject a system because it lacks a high-end CPU
    or GPU. A dedicated GPU is not automatically required for cloud-based
    work. Consider actual workload needs of the team.

    Do not approve a system just because one or two specifications look good.
    Explain genuine bottlenecks and their practical impact.
    Do not invent specifications that were not supplied.
    If critical configuration details are missing or ambiguous, do not
    confidently approve; request manual verification in the result.
    """

    price_guide = """
    Approximate India cost guide, INR:
    RAM upgrade to 16 GB: Rs 2,500-5,000.
    256-512 GB SSD: Rs 2,500-5,000.
    New laptop with Core i5/Ryzen 5, 16 GB RAM and 512 GB SSD:
    Rs 45,000-65,000.
    Broadband/fiber: Rs 600-1,200 per month.

    These are rough estimates, not live quotes. Upgrade compatibility
    and actual prices depend on the laptop model and location.
    """

    # ---------------- Gemini call: fail fast, respect the deadline ----------------
    def ask_json(prompt):
        generation_config = {
            "temperature": 0,
            "responseMimeType": "application/json",
            "maxOutputTokens": 800,
        }

        thinking = {}
        level = os.environ.get("AI_THINKING_LEVEL", "").strip()
        budget = os.environ.get("AI_THINKING_BUDGET", "").strip()
        if level:
            thinking["thinkingLevel"] = level
        elif budget:
            try:
                thinking["thinkingBudget"] = int(budget)
            except ValueError:
                pass
        if thinking:
            generation_config["thinkingConfig"] = thinking

        last_error = None

        for attempt in range(2):
            remaining = deadline - time.time()
            if remaining < 5:
                raise TimeoutError("time budget used up")

            try:
                response = requests.post(
                    gemini_url,
                    headers={
                        "x-goog-api-key": api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "systemInstruction": {
                            "parts": [{"text": system_instruction}]
                        },
                        "contents": [
                            {"role": "user", "parts": [{"text": prompt}]}
                        ],
                        "generationConfig": generation_config,
                    },
                    timeout=(5, min(max_read_timeout, remaining)),
                )

                # 429 = quota/rate limit: retrying right away will not help
                if response.status_code == 429:
                    raise RuntimeError("Gemini quota/rate limit (429)")

                # 503 = Google overloaded: one quick retry only
                if response.status_code == 503:
                    last_error = "Gemini overloaded (503)"
                    time.sleep(2)
                    continue

                response.raise_for_status()

                body = response.json()
                candidates = body.get("candidates") or []
                if not candidates:
                    raise RuntimeError(
                        "Gemini returned no candidates: "
                        + str(body.get("promptFeedback", ""))
                    )

                parts = candidates[0].get("content", {}).get("parts") or []
                content = "".join(part.get("text", "") for part in parts)
                content = (
                    content.replace("```json", "").replace("```", "").strip()
                )
                return json.loads(content)

            except requests.exceptions.Timeout as exc:
                last_error = "Gemini timeout: " + str(exc)
                break
            except Exception as exc:
                last_error = str(exc)
                if "429" in last_error:
                    break
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status is not None and 400 <= status < 500:
                    break

        raise RuntimeError("Gemini request failed: " + str(last_error))

    def clean(value):
        # Tableau can send None for NULL values
        return "" if value is None else str(value).strip()

    pending_text = (
        "⏳ PENDING\n\n"
        "📌 Reason: AI assessment is still in progress. "
        "Please refresh the dashboard in a minute."
    )

    output = []
    cache_changed = False

    for cpu, ram, storage, internet, system_type, team, owner in zip(
        cpus, rams, storages, nets, sys_types, teams, system_owners
    ):
        owner_key = clean(owner).lower()
        team_key = clean(team).upper()

        # ---- Company system: no check needed, always approved ----
        if owner_key == "company system":
            output.append("Approved")
            continue

        # ---- Unknown owner value: never silently approve ----
        if owner_key != "personal system":
            output.append(
                "⚠️ MANUAL REVIEW\n\n"
                "📌 Reason: System type (Personal/Company) is missing or invalid."
            )
            continue

        # ---- Personal system: cached or full AI check ----
        key = "||".join(
            [
                clean(cpu),
                clean(ram),
                clean(storage),
                clean(internet),
                clean(system_type),
                team_key,
            ]
        )

        if key in cache:
            output.append(cache[key])
            continue

        # Out of time for this Tableau call: leave for the next refresh
        if time.time() > deadline - 5:
            output.append(pending_text)
            continue

        configuration = {
            "CPU": str(cpu),
            "RAM": str(ram),
            "Storage": str(storage),
            "Internet": str(internet),
            "System type": str(system_type),
            "Team": clean(team) or "Unknown",
            "Ownership": "Personal System",
        }

        work_description = team_work.get(team_key, generic_work)

        prompt = f"""
        {base_requirements}

        EMPLOYEE TEAM AND WORK:
        {work_description}

        PRICE GUIDE:
        {price_guide}

        LAPTOP CONFIGURATION:
        {json.dumps(configuration, ensure_ascii=False)}

        Make one overall decision for this configuration and the described
        team work.

        Decision rules:
        1. If the supplied configuration is reasonably suitable for this
           team's work, return decision "APPROVED".
        2. If it is not suitable, return decision "NOT SUITABLE" and explain
           the specific bottleneck, why it matters for this team's work, what
           to upgrade or change, and approximate cost when reasonably
           estimable.
        3. If important information is missing and suitability cannot be
           established, return decision "MANUAL REVIEW". State exactly
           what information must be checked.
        4. Prefer targeted upgrades over buying a new laptop when practical.
        5. If CPU limitations require replacing the laptop, explain why.
        6. Consider cloud processing versus local processing.
        7. Do not make up RAM, CPU generation, SSD type, internet speed,
           laptop model or other missing details.
        8. Do not treat a dedicated GPU as mandatory unless the described
           team workload actually needs one.
        9. Be specific. Avoid generic advice such as "upgrade your system"
           without saying what is wrong and why.
        10. Write every field in simple, clear English. Keep each field to
            one or two short sentences. Use plain text, no Markdown, no
            bullet symbols, no line breaks and no pipe character inside
            any text field.

        Return only valid JSON in this exact structure:
        {{
          "decision": "APPROVED or NOT SUITABLE or MANUAL REVIEW",
          "reason": "Why the system is or is not suitable for this team",
          "impact": "Practical impact on this team's work",
          "upgrades": "Specific recommended changes, or None",
          "estimated_cost": "Approximate INR cost, or Cannot estimate",
          "missing_information": "Details that need verification, or None"
        }}
        """

        failed = False

        try:
            data = ask_json(prompt)

            decision = str(data.get("decision", "")).strip().upper()

            if decision == "APPROVED":
                result = "Approved"

            elif decision in ("NOT SUITABLE", "MANUAL REVIEW"):
                reason = str(data.get("reason", "")).strip()
                impact = str(data.get("impact", "")).strip()
                upgrades = str(data.get("upgrades", "")).strip()
                cost = str(data.get("estimated_cost", "")).strip()
                missing = str(data.get("missing_information", "")).strip()

                icon = "❌" if decision == "NOT SUITABLE" else "⚠️"
                team_label = clean(team) or "Unknown"

                parts = [
                    icon + " " + decision + " - Team: " + team_label,
                    "",
                    "📌 Reason: " + (reason or "AI did not provide a reason."),
                    "💼 Work Impact: " + (impact or "Impact needs verification."),
                    "🔧 Recommended Upgrade: " + (upgrades or "Needs assessment."),
                    "💰 Approx Cost: " + (cost or "Cannot estimate"),
                ]

                if missing and missing.lower() not in ("none", "n/a"):
                    parts.append("🔍 Please Verify: " + missing)

                result = "\n".join(parts)

            else:
                failed = True
                result = (
                    "⚠️ MANUAL REVIEW\n\n"
                    "📌 Reason: AI returned an invalid decision. "
                    "Please verify the configuration manually."
                )

        except TimeoutError:
            # Budget ran out mid-loop: not an error, just try again next refresh
            output.append(pending_text)
            continue

        except Exception as exc:
            print("AI ERROR:", repr(exc))
            failed = True
            result = (
                "⚠️ MANUAL REVIEW\n\n"
                "📌 Reason: AI assessment failed (temporary). "
                "Refresh the dashboard to retry."
            )

        # Keep line breaks, but clean extra spaces and pipe characters per line
        result = "\n".join(
            " ".join(line.replace("|", "/").split()) for line in result.split("\n")
        )

        output.append(result)

        # Cache only successful AI answers, never failures
        if not failed:
            cache[key] = result
            cache_changed = True
            save_cache(cache)

    return output


# --------------------------------------------------
# 3. Deploy the function to TabPy
# --------------------------------------------------
tabpy_user = os.environ.get("TABPY_USER")
tabpy_pass = os.environ.get("TABPY_PASS")

if not tabpy_user or not tabpy_pass:
    raise RuntimeError("TABPY_USER or TABPY_PASS missing from .env")

if not os.environ.get("AI_API_KEY"):
    raise RuntimeError("AI_API_KEY missing from .env")

if not os.environ.get("AI_MODEL"):
    raise RuntimeError("AI_MODEL missing from .env")

client = Client("http://localhost:9004/")
client.set_credentials(tabpy_user, tabpy_pass)

client.deploy(
    "check_system",
    check_system,
    "AI-based laptop suitability assessment by team (Personal systems only)",
    override=True,
)

print("SUCCESS: AI-based check_system endpoint deployed.")
