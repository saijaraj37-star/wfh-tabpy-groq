# import os
# import json
# import time
# import requests
# from tabpy.tabpy_tools.client import Client


# # --------------------------------------------------
# # 1. Load .env from the same folder as this script
# # --------------------------------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ENV_FILE = os.path.join(BASE_DIR, ".env")

# if os.path.isfile(ENV_FILE):
#     with open(ENV_FILE, "r", encoding="utf-8") as env_file:
#         for line in env_file:
#             line = line.strip()

#             if not line or line.startswith("#") or "=" not in line:
#                 continue

#             name, value = line.split("=", 1)
#             name = name.strip()
#             value = value.strip().strip('"').strip("'")

#             if name and name not in os.environ:
#                 os.environ[name] = value


# # --------------------------------------------------
# # 2. AI-based complete system assessment
# #    Company System  -> Approved (no AI check)
# #    Personal System -> Full AI check based on team work
# # --------------------------------------------------
# def check_system(cpus, rams, storages, nets, sys_types, teams, system_owners):
#     model = os.environ["AI_MODEL"]
#     api_key = os.environ["AI_API_KEY"]

#     groq_url = "https://api.groq.com/openai/v1/chat/completions"

#     # Team-wise work profile. Edit these as per your real team work.
#     team_work = {
#         "CSA": """
#         Team CSA work:
#         - Client/support analysis, reporting and data validation.
#         - SQL queries on BigQuery, Excel/Sheets, dashboards.
#         - Browser tabs, video meetings, office applications.
#         - Light Python/VS Code usage.
#         """,
#         "CUBE": """
#         Team Cube work:
#         - Cube (semantic layer) development, Node.js and YAML/JS models.
#         - BigQuery/GCP connections, API testing.
#         - Docker containers for local Cube setup, VS Code, terminals.
#         - Browser, Postman-type tools and video meetings.
#         """,
#         "DATA MART": """
#         Team Data Mart work:
#         - BigQuery SQL, data modeling and data mart pipelines on GCP.
#         - Python, notebooks, VS Code, dbt-style transformations.
#         - Validating large result sets, many browser tabs and meetings.
#         """,
#         "EDW": """
#         Team EDW work:
#         - Enterprise data warehouse design, ETL/ELT pipelines on GCP.
#         - Heavy SQL, large extracts and comparisons, SQL clients.
#         - Python scripts, Airflow/orchestration tools, GCP Console.
#         - Heavy multitasking with many tabs and applications.
#         """,
#         "LLM": """
#         Team LLM work:
#         - AI/LLM application development, mostly via cloud APIs.
#         - Python, notebooks, embeddings, vector data, Docker.
#         - Occasional small local model testing.
#         - A dedicated GPU is needed only if large local models are
#           trained or run locally; cloud GPU/API usage does not need it.
#         """,
#         "LOOKER": """
#         Team Looker work:
#         - LookML development in browser IDE, dashboards and reporting.
#         - Many browser tabs open together, Git, BigQuery, video meetings.
#         - Browser heavy workload, so RAM and stable internet matter most.
#         """,
#         "OPS": """
#         Team OPS work:
#         - Cloud and pipeline monitoring, GCP Console, logs and alerts.
#         - Terminals, scripts, incident handling over video calls.
#         - Stable internet is critical; compute need is moderate.
#         """,
#         "QA": """
#         Team QA work:
#         - Data and application testing, test automation scripts.
#         - Multiple browsers, Selenium/Playwright style tools, Docker.
#         - BigQuery validation queries, Python, VS Code, meetings.
#         """,
#         "UI/UX": """
#         Team UI/UX work:
#         - Design tools such as Figma, prototyping, image/asset editing.
#         - Many browser tabs, large design files, video meetings.
#         - Smooth graphics, good RAM and fast SSD matter; display quality
#           and integrated/dedicated GPU capability can matter more here.
#         """,
#     }

#     generic_work = """
#     Team not recognised. Assume a general data engineering and analytics
#     employee (GCP, BigQuery, Looker, Python, VS Code, browser tabs, meetings).
#     """

#     base_requirements = """
#     Assess a personal laptop that an employee wants to use for office work
#     from home.

#     Important workload distinction:
#     Heavy data processing can run on GCP cloud infrastructure.
#     Do not assume the laptop must process all cloud data locally.
#     However, local development, Docker, multitasking and large local datasets
#     still require adequate laptop resources.

#     Assess the COMPLETE configuration together, not just one component
#     against a rigid checklist. Consider CPU generation and capability,
#     available RAM, storage capacity and type, internet suitability,
#     and whether the configuration can realistically support the
#     team's work described above.

#     Do not automatically reject a system because it lacks a high-end CPU
#     or GPU. A dedicated GPU is not automatically required for cloud-based
#     work. Consider actual workload needs of the team.

#     Do not approve a system just because one or two specifications look good.
#     Explain genuine bottlenecks and their practical impact.
#     Do not invent specifications that were not supplied.
#     If critical configuration details are missing or ambiguous, do not
#     confidently approve; request manual verification in the result.
#     """

#     price_guide = """
#     Approximate India cost guide, INR:
#     RAM upgrade to 16 GB: Rs 2,500-5,000.
#     256-512 GB SSD: Rs 2,500-5,000.
#     New laptop with Core i5/Ryzen 5, 16 GB RAM and 512 GB SSD:
#     Rs 45,000-65,000.
#     Broadband/fiber: Rs 600-1,200 per month.

#     These are rough estimates, not live quotes. Upgrade compatibility
#     and actual prices depend on the laptop model and location.
#     """

#     def ask_json(prompt):
#         last_error = None

#         for attempt in range(4):
#             try:
#                 response = requests.post(
#                     groq_url,
#                     headers={
#                         "Authorization": "Bearer " + api_key,
#                         "Content-Type": "application/json",
#                     },
#                     json={
#                         "model": model,
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": (
#                                     "You are a careful IT hardware assessor. "
#                                     "Be practical, technically accurate and "
#                                     "honest about uncertainty. Never invent "
#                                     "hardware specifications."
#                                 ),
#                             },
#                             {"role": "user", "content": prompt},
#                         ],
#                         "response_format": {"type": "json_object"},
#                         "temperature": 0,
#                     },
#                     timeout=60,
#                 )

#                 if response.status_code == 429:
#                     last_error = "Groq rate limit (429)"

#                     if attempt < 3:
#                         time.sleep(10 * (attempt + 1))
#                         continue

#                     raise RuntimeError(last_error)

#                 response.raise_for_status()

#                 content = response.json()["choices"][0]["message"]["content"]
#                 return json.loads(content)

#             except Exception as exc:
#                 last_error = str(exc)

#                 status_code = getattr(
#                     getattr(exc, "response", None),
#                     "status_code",
#                     None,
#                 )

#                 if (
#                     status_code is not None
#                     and 400 <= status_code < 500
#                     and status_code != 429
#                 ):
#                     raise

#                 if attempt == 3:
#                     raise RuntimeError(
#                         "Groq request failed: " + last_error
#                     ) from exc

#                 time.sleep(2 * (attempt + 1))

#         raise RuntimeError("Groq request failed: " + str(last_error))

#     def clean(value):
#         # Tableau can send None for NULL values
#         return "" if value is None else str(value).strip()

#     # Cache avoids repeating identical assessments within one invocation.
#     cache = {}
#     output = []

#     for cpu, ram, storage, internet, system_type, team, owner in zip(
#         cpus, rams, storages, nets, sys_types, teams, system_owners
#     ):
#         owner_key = clean(owner).lower()
#         team_key = clean(team).upper()

#         # ---- Company system: no check needed, always approved ----
#         if owner_key == "company system":
#             output.append("Approved")
#             continue

#         # ---- Unknown owner value: never silently approve ----
#         if owner_key != "personal system":
#             output.append(
#                 "⚠️ MANUAL REVIEW\n\n"
#                 "📌 Reason: System type (Personal/Company) is missing or invalid."
#             )
#             continue

#         # ---- Personal system: full AI check based on team work ----
#         key = (cpu, ram, storage, internet, system_type, team_key)

#         if key in cache:
#             output.append(cache[key])
#             continue

#         configuration = {
#             "CPU": str(cpu),
#             "RAM": str(ram),
#             "Storage": str(storage),
#             "Internet": str(internet),
#             "System type": str(system_type),
#             "Team": clean(team) or "Unknown",
#             "Ownership": "Personal System",
#         }

#         work_description = team_work.get(team_key, generic_work)

#         prompt = f"""
#         {base_requirements}

#         EMPLOYEE TEAM AND WORK:
#         {work_description}

#         PRICE GUIDE:
#         {price_guide}

#         LAPTOP CONFIGURATION:
#         {json.dumps(configuration, ensure_ascii=False)}

#         Make one overall decision for this configuration and the described
#         team work.

#         Decision rules:
#         1. If the supplied configuration is reasonably suitable for this
#            team's work, return decision "APPROVED".
#         2. If it is not suitable, return decision "NOT SUITABLE" and explain
#            the specific bottleneck, why it matters for this team's work, what
#            to upgrade or change, and approximate cost when reasonably
#            estimable.
#         3. If important information is missing and suitability cannot be
#            established, return decision "MANUAL REVIEW". State exactly
#            what information must be checked.
#         4. Prefer targeted upgrades over buying a new laptop when practical.
#         5. If CPU limitations require replacing the laptop, explain why.
#         6. Consider cloud processing versus local processing.
#         7. Do not make up RAM, CPU generation, SSD type, internet speed,
#            laptop model or other missing details.
#         8. Do not treat a dedicated GPU as mandatory unless the described
#            team workload actually needs one.
#         9. Be specific. Avoid generic advice such as "upgrade your system"
#            without saying what is wrong and why.
#         10. Write every field in simple, clear English. Keep each field to
#             one or two short sentences. Use plain text, no Markdown, no
#             bullet symbols, no line breaks and no pipe character inside
#             any text field.

#         Return only valid JSON in this exact structure:
#         {{
#           "decision": "APPROVED or NOT SUITABLE or MANUAL REVIEW",
#           "reason": "Why the system is or is not suitable for this team",
#           "impact": "Practical impact on this team's work",
#           "upgrades": "Specific recommended changes, or None",
#           "estimated_cost": "Approximate INR cost, or Cannot estimate",
#           "missing_information": "Details that need verification, or None"
#         }}
#         """

#         try:
#             data = ask_json(prompt)

#             decision = str(data.get("decision", "")).strip().upper()

#             if decision == "APPROVED":
#                 result = "Approved"

#             elif decision in ("NOT SUITABLE", "MANUAL REVIEW"):
#                 reason = str(data.get("reason", "")).strip()
#                 impact = str(data.get("impact", "")).strip()
#                 upgrades = str(data.get("upgrades", "")).strip()
#                 cost = str(data.get("estimated_cost", "")).strip()
#                 missing = str(data.get("missing_information", "")).strip()

#                 icon = "❌" if decision == "NOT SUITABLE" else "⚠️"
#                 team_label = clean(team) or "Unknown"

#                 parts = [
#                     icon + " " + decision + " - Team: " + team_label,
#                     "",
#                     "📌 Reason: " + (reason or "AI did not provide a reason."),
#                     "💼 Work Impact: " + (impact or "Impact needs verification."),
#                     "🔧 Recommended Upgrade: " + (upgrades or "Needs assessment."),
#                     "💰 Approx Cost: " + (cost or "Cannot estimate"),
#                 ]

#                 if missing and missing.lower() not in ("none", "n/a"):
#                     parts.append("🔍 Please Verify: " + missing)

#                 result = "\n".join(parts)

#             else:
#                 # Unknown output must never be silently approved.
#                 result = (
#                     "⚠️ MANUAL REVIEW\n\n"
#                     "📌 Reason: AI returned an invalid decision. "
#                     "Please verify the configuration manually."
#                 )

#         except Exception as exc:
#             print("AI ERROR:", repr(exc))
#             result = (
#                 "⚠️ MANUAL REVIEW\n\n"
#                 "📌 Reason: AI assessment failed. "
#                 "Check the Groq API, model and logs."
#             )

#         # Keep line breaks, but clean extra spaces and pipe characters per line
#         result = "\n".join(
#             " ".join(line.replace("|", "/").split()) for line in result.split("\n")
#         )

#         cache[key] = result
#         output.append(result)

#     return output


# # --------------------------------------------------
# # 3. Deploy the function to TabPy
# # --------------------------------------------------
# tabpy_user = os.environ.get("TABPY_USER")
# tabpy_pass = os.environ.get("TABPY_PASS")

# if not tabpy_user or not tabpy_pass:
#     raise RuntimeError("TABPY_USER or TABPY_PASS missing from .env")

# if not os.environ.get("AI_API_KEY"):
#     raise RuntimeError("AI_API_KEY missing from .env")

# if not os.environ.get("AI_MODEL"):
#     raise RuntimeError("AI_MODEL missing from .env")

# client = Client("http://localhost:9004/")
# client.set_credentials(tabpy_user, tabpy_pass)

# client.deploy(
#     "check_system",
#     check_system,
#     "AI-based laptop suitability assessment by team (Personal systems only)",
#     override=True,
# )

# print("SUCCESS: AI-based check_system endpoint deployed.")

import os
import json
import time
import requests
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
# 2. AI-based complete system assessment
#    Company System  -> Approved (no AI check)
#    Personal System -> Full AI check based on team work
#
#    Everything the function needs is defined INSIDE it,
#    so TabPy can serialize and deploy it as one unit.
# --------------------------------------------------
def check_system(cpus, rams, storages, nets, sys_types, teams, system_owners):
    model = os.environ["AI_MODEL"]
    api_key = os.environ["AI_API_KEY"]

    groq_url = "https://api.groq.com/openai/v1/chat/completions"

    # ----------------------------------------------
    # Team-wise work profile.
    # Only list tools the team REALLY uses. The AI is told
    # to mention only tools that appear in these lists.
    # ----------------------------------------------
    team_work = {
        "CSA": """
        Team CSA work:
        - Client/support analysis, reporting and data validation.
        - SQL queries on BigQuery, Excel/Sheets, dashboards.
        - Browser tabs, video meetings, office applications.
        - Light Python and VS Code usage.
        """,
        "CUBE": """
        Team Cube work:
        - Cube (semantic layer) development with Node.js and YAML/JS models.
        - BigQuery/GCP connections, API testing.
        - VS Code, terminals, Git.
        - Browser tabs and video meetings.
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
        - Python, notebooks, embeddings, vector data, VS Code.
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
        - Multiple browsers, Selenium/Playwright style tools.
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

    # Company baseline used as a reference for each spec check.
    # Edit this block if the company minimum changes.
    company_baseline = """
    Company baseline for personal systems (reference for the spec check):
    - CPU: Intel Core i5 or AMD Ryzen 5, or higher.
    - RAM: 16 GB or higher.
    - Storage: 256 GB SSD or higher.
    - Internet: stable broadband, fiber or wired connection.
      Mobile internet or hotspot is NOT permitted.
    A spec below the baseline is a GAP unless the team work clearly makes
    it acceptable. State the reason in the note.
    """

    # Team-wise requirement. One short line per team.
    # This is shown in the report and used by the AI for the spec check.
    # The company baseline above is the minimum for everyone; a team line
    # can only be equal or stricter. EDIT THESE VALUES to match each team.
    team_requirement = {
        "CSA": "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 256 GB+, stable broadband/fiber",
        "CUBE": "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 256 GB+, stable broadband/fiber",
        "DATA MART": "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 512 GB+, stable broadband/fiber",
        "EDW": "CPU i5/Ryzen 5+, RAM 16 GB+ (32 GB preferred), SSD 512 GB+, stable broadband/fiber",
        "LLM": "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 512 GB+, stable broadband/fiber (GPU not needed for cloud APIs)",
        "LOOKER": "CPU i5/Ryzen 5+, RAM 16 GB+ (browser heavy), SSD 256 GB+, stable broadband/fiber",
        "OPS": "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 256 GB+, wired or fiber internet (critical)",
        "QA": "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 512 GB+, stable broadband/fiber",
        "UI/UX": "CPU i5/Ryzen 5+, RAM 16 GB+ (32 GB preferred), SSD 512 GB+, capable graphics, stable broadband/fiber",
    }

    # One-line work summary per team, shown in the Approved details.
    team_work_summary = {
        "CSA": "Client/support analysis, reporting, BigQuery SQL, dashboards, meetings",
        "CUBE": "Cube semantic layer development (Node.js, YAML/JS), BigQuery/GCP, API testing",
        "DATA MART": "BigQuery SQL, data modeling, data mart pipelines on GCP, Python notebooks",
        "EDW": "Warehouse design, ETL/ELT pipelines on GCP, heavy SQL, orchestration tools",
        "LLM": "LLM application development via cloud APIs, Python, notebooks, embeddings",
        "LOOKER": "LookML development, dashboards, many browser tabs, meetings",
        "OPS": "Cloud and pipeline monitoring, logs, alerts, incident calls",
        "QA": "Data and application testing, test automation, BigQuery validation",
        "UI/UX": "Figma design, prototyping, image/asset editing, large design files",
    }

    default_requirement = (
        "CPU i5/Ryzen 5+, RAM 16 GB+, SSD 256 GB+, "
        "stable broadband/fiber/wired internet (hotspot not permitted)"
    )

    base_requirements = """
    Assess a personal laptop that an employee wants to use for office work
    from home.

    Important workload distinction:
    Heavy data processing runs on GCP cloud infrastructure. Do not assume
    the laptop must process all cloud data locally.

    Assess the COMPLETE configuration together. Consider CPU generation and
    capability, RAM, storage capacity and type, internet suitability, and
    whether the configuration can realistically support the team's work.

    Do not automatically reject a system because it lacks a high-end CPU
    or GPU. A dedicated GPU is not required for cloud-based work.

    Do not approve a system just because one or two specifications look good.
    Do not invent specifications that were not supplied.
    If critical configuration details are missing or ambiguous, do not
    confidently approve; request manual verification.
    """

    tool_rules = """
    TOOL RULES (important):
    - Only mention software or tools that appear in the team work
      description above.
    - Never mention Docker, containers, virtual machines, WSL, local model
      training or gaming. These tools are not used by these teams.
    - Do not add generic advice that is not tied to the team's real work.
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

    # ----------------------------------------------
    # Helpers
    # ----------------------------------------------
    def ask_json(prompt):
        last_error = None

        for attempt in range(4):
            try:
                response = requests.post(
                    groq_url,
                    headers={
                        "Authorization": "Bearer " + api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a careful IT hardware assessor. "
                                    "Be practical, technically accurate and "
                                    "honest about uncertainty. Never invent "
                                    "hardware specifications."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0,
                    },
                    timeout=60,
                )

                if response.status_code == 429:
                    last_error = "Groq rate limit (429)"

                    if attempt < 3:
                        time.sleep(10 * (attempt + 1))
                        continue

                    raise RuntimeError(last_error)

                response.raise_for_status()

                content = response.json()["choices"][0]["message"]["content"]
                return json.loads(content)

            except Exception as exc:
                last_error = str(exc)

                status_code = getattr(
                    getattr(exc, "response", None),
                    "status_code",
                    None,
                )

                if (
                    status_code is not None
                    and 400 <= status_code < 500
                    and status_code != 429
                ):
                    raise

                if attempt == 3:
                    raise RuntimeError(
                        "Groq request failed: " + last_error
                    ) from exc

                time.sleep(2 * (attempt + 1))

        raise RuntimeError("Groq request failed: " + str(last_error))

    def clean(value):
        # Tableau can send None for NULL values
        return "" if value is None else str(value).strip()

    def short(value, default=""):
        # One-line text: collapse spaces/newlines, remove pipe characters
        text = " ".join(str(value if value is not None else "").split())
        text = text.replace("|", "/")
        return text or default

    def is_empty_text(text):
        return text.strip().lower() in ("", "none", "n/a", "na", "nil", "-")

    def to_int(value):
        try:
            number = int(float(value))
            return number if number >= 0 else None
        except (TypeError, ValueError):
            return None

    def inr(number):
        # Indian digit grouping: 1,25,000
        digits = str(int(number))
        if len(digits) <= 3:
            return "Rs " + digits
        last3, rest = digits[-3:], digits[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        return "Rs " + ",".join(groups + [last3])

    def cost_text(low, high):
        if low is not None and high is not None:
            if high < low:
                low, high = high, low
            if low == high:
                return "Approx " + inr(low)
            return "Approx " + inr(low) + " - " + inr(high)
        if low is not None:
            return "From approx " + inr(low)
        if high is not None:
            return "Up to approx " + inr(high)
        return "Cost cannot be estimated"

    status_labels = {
        "OK": "✅ OK",
        "GAP": "❌ GAP",
        "UNKNOWN": "❓ VERIFY",
    }

    def get_status(item):
        status = str((item or {}).get("status", "")).strip().upper()
        return status if status in status_labels else "UNKNOWN"

    def build_report(data, decision, team_label, team_req):
        icon = "❌" if decision == "NOT SUITABLE" else "⚠️"
        spec = data.get("spec_check") or {}

        lines = [
            icon + " " + decision + " - Team: " + team_label,
            "",
            "Summary: " + short(data.get("summary"), "No summary provided."),
            "",
            "TEAM REQUIREMENT",
            team_req,
            "",
            "SPEC CHECK",
        ]

        for label, key in (
            ("CPU", "cpu"),
            ("RAM", "ram"),
            ("Storage", "storage"),
            ("Internet", "internet"),
        ):
            item = spec.get(key) or {}
            status = status_labels[get_status(item)]
            note = short(item.get("note"), "No details provided.")
            lines.append(label + ": " + status + " - " + note)

        lines += [
            "",
            "WORK IMPACT",
            short(data.get("impact"), "Impact needs verification."),
        ]

        # Recommended actions with per-item and total cost
        actions = data.get("actions")
        actions = actions if isinstance(actions, list) else []
        actions = [a for a in actions if isinstance(a, dict)][:4]

        lines += ["", "RECOMMENDED ACTIONS"]

        total_low = 0
        total_high = 0
        costed = 0
        uncosted = 0

        if not actions:
            lines.append("No specific action suggested. Needs manual assessment.")

        for number, item in enumerate(actions, start=1):
            low = to_int(item.get("cost_min_inr"))
            high = to_int(item.get("cost_max_inr"))

            if low is None and high is not None:
                low = high
            if high is None and low is not None:
                high = low

            if low is not None and high is not None:
                total_low += min(low, high)
                total_high += max(low, high)
                costed += 1
            else:
                uncosted += 1

            lines.append(
                str(number)
                + ". "
                + short(item.get("action"), "Action not described.")
                + " ("
                + cost_text(low, high)
                + ")"
            )

        if costed > 0:
            total_line = "TOTAL APPROX COST: " + cost_text(total_low, total_high).replace("Approx ", "", 1)
            if uncosted > 0:
                total_line += " (excludes items that cannot be estimated)"
            lines += ["", total_line]

        missing = short(data.get("missing_information"))
        if not is_empty_text(missing):
            lines += ["", "PLEASE VERIFY", missing]

        return "\n".join(lines)

    def build_approved(team_label, team_key, owner_label, data=None):
        work = team_work_summary.get(team_key, "Team not listed")
        req = team_requirement.get(team_key, default_requirement)

        lines = [
            "Approved",
            "",
            "TEAM: " + team_label + " (" + owner_label + ")",
            "",
            "WORK",
            work,
            "",
            "MINIMUM REQUIREMENT FOR THIS WORK",
            req,
        ]

        if data is not None:
            # Personal system: also show the spec-by-spec result
            spec = data.get("spec_check") or {}
            lines += ["", "SPEC CHECK"]
            for label, key in (
                ("CPU", "cpu"),
                ("RAM", "ram"),
                ("Storage", "storage"),
                ("Internet", "internet"),
            ):
                item = spec.get(key) or {}
                lines.append(
                    label
                    + ": "
                    + status_labels[get_status(item)]
                    + " - "
                    + short(item.get("note"), "Meets the requirement.")
                )
            summary = short(data.get("summary"))
            if summary:
                lines += ["", "Summary: " + summary]
        else:
            lines += [
                "",
                "Company system: no personal-system check needed. "
                "Internet at home must still be stable broadband, fiber "
                "or wired; mobile internet or hotspot is not permitted.",
            ]

        return "\n".join(lines)

    # Cache avoids repeating identical assessments within one invocation.
    cache = {}
    output = []

    for cpu, ram, storage, internet, system_type, team, owner in zip(
        cpus, rams, storages, nets, sys_types, teams, system_owners
    ):
        owner_key = clean(owner).lower()
        team_key = clean(team).upper()

        # ---- Company system: no check needed, always approved ----
        if owner_key == "company system":
            output.append(
                build_approved(clean(team) or "Unknown", team_key, "Company System")
            )
            continue

        # ---- Unknown owner value: never silently approve ----
        if owner_key != "personal system":
            output.append(
                "⚠️ MANUAL REVIEW\n\n"
                "Summary: System type (Personal/Company) is missing or invalid."
            )
            continue

        # ---- Personal system: full AI check based on team work ----
        key = (cpu, ram, storage, internet, system_type, team_key)

        if key in cache:
            output.append(cache[key])
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

        team_label = clean(team) or "Unknown"
        work_description = team_work.get(team_key, generic_work)
        team_req = team_requirement.get(
            team_key, "Use the company baseline only (team not recognised)."
        )

        prompt = f"""
        {base_requirements}

        EMPLOYEE TEAM AND WORK:
        {work_description}

        {tool_rules}

        {company_baseline}

        TEAM REQUIREMENT FOR THIS TEAM (use it for the spec check):
        {team_req}

        PRICE GUIDE:
        {price_guide}

        LAPTOP CONFIGURATION:
        {json.dumps(configuration, ensure_ascii=False)}

        Make one overall decision for this configuration and the described
        team work.

        Decision rules:
        1. Return "APPROVED" only if the configuration is reasonably suitable
           for this team's work AND no spec_check item is a GAP.
        2. Return "NOT SUITABLE" if at least one real bottleneck would hurt
           this team's work.
        3. Return "MANUAL REVIEW" if important information is missing and
           suitability cannot be established.
        4. For each of cpu, ram, storage and internet, set status to
           OK, GAP or UNKNOWN, judged against the TEAM REQUIREMENT above. Write a short note naming the actual value
           supplied (for example "8 GB, below the 16 GB baseline").
           Do not invent values that were not supplied.
        5. Prefer targeted upgrades over buying a new laptop when practical.
           If the CPU forces a laptop replacement, list ONLY the replacement
           as one action, not the component upgrades as well. Actions must
           not overlap, so their costs can be added up.
        6. Give at most 3 actions. Every action must name what to change and
           why, tied to this team's real work.
        7. For each action give cost_min_inr and cost_max_inr as whole
           numbers in INR (one-time cost, no monthly values), or null if it
           cannot be estimated.
        8. Do not treat a dedicated GPU as mandatory unless the team work
           actually needs one.
        9. Write every text field in simple, clear English, one short
           sentence each. Use plain text only: no Markdown, no bullet
           symbols, no line breaks and no pipe character.
        10. If decision is APPROVED, actions must be an empty list.

        Return only valid JSON in this exact structure:
        {{
          "decision": "APPROVED or NOT SUITABLE or MANUAL REVIEW",
          "summary": "One sentence overall verdict for this team",
          "spec_check": {{
            "cpu": {{"status": "OK or GAP or UNKNOWN", "note": "short note"}},
            "ram": {{"status": "OK or GAP or UNKNOWN", "note": "short note"}},
            "storage": {{"status": "OK or GAP or UNKNOWN", "note": "short note"}},
            "internet": {{"status": "OK or GAP or UNKNOWN", "note": "short note"}}
          }},
          "impact": "How the gaps affect this team's daily work",
          "actions": [
            {{"action": "What to change and why", "cost_min_inr": 0, "cost_max_inr": 0}}
          ],
          "missing_information": "Details that need verification, or None"
        }}
        """

        try:
            data = ask_json(prompt)

            decision = str(data.get("decision", "")).strip().upper()

            spec = data.get("spec_check") or {}
            has_gap = any(
                get_status(spec.get(k)) == "GAP"
                for k in ("cpu", "ram", "storage", "internet")
            )

            if decision == "APPROVED" and has_gap:
                # AI said approved but flagged a gap: never silently approve.
                decision = "MANUAL REVIEW"
                data["summary"] = (
                    "AI result was inconsistent (approved with a gap). "
                    "Please verify manually."
                )

            if decision == "APPROVED":
                result = build_approved(
                    team_label, team_key, "Personal System", data
                )

            elif decision in ("NOT SUITABLE", "MANUAL REVIEW"):
                result = build_report(data, decision, team_label, team_req)

            else:
                # Unknown output must never be silently approved.
                result = (
                    "⚠️ MANUAL REVIEW\n\n"
                    "Summary: AI returned an invalid decision. "
                    "Please verify the configuration manually."
                )

        except Exception as exc:
            print("AI ERROR:", repr(exc))
            result = (
                "⚠️ MANUAL REVIEW\n\n"
                "Summary: AI assessment failed. "
                "Check the Groq API, model and logs."
            )

        # Keep line breaks, but clean extra spaces and pipe characters per line
        result = "\n".join(
            " ".join(line.replace("|", "/").split()) for line in result.split("\n")
        )

        cache[key] = result
        output.append(result)

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

client = Client(os.environ.get("TABPY_URL", "http://localhost:9004/"))
client.set_credentials(tabpy_user, tabpy_pass)

client.deploy(
    "check_system",
    check_system,
    "AI-based laptop suitability assessment by team (Personal systems only)",
    override=True,
)

print("SUCCESS: AI-based check_system endpoint deployed.")
