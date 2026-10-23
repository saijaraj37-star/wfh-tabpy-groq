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
# --------------------------------------------------
def check_system(cpus, rams, storages, nets, sys_types, teams, system_owners):
    model = os.environ["AI_MODEL"]
    api_key = os.environ["AI_API_KEY"]

    groq_url = "https://api.groq.com/openai/v1/chat/completions"

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
            output.append("Approved")
            continue

        # ---- Unknown owner value: never silently approve ----
        if owner_key != "personal system":
            output.append(
                "⚠️ MANUAL REVIEW\n\n"
                "📌 Reason: System type (Personal/Company) is missing or invalid."
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
                # Unknown output must never be silently approved.
                result = (
                    "⚠️ MANUAL REVIEW\n\n"
                    "📌 Reason: AI returned an invalid decision. "
                    "Please verify the configuration manually."
                )

        except Exception as exc:
            print("AI ERROR:", repr(exc))
            result = (
                "⚠️ MANUAL REVIEW\n\n"
                "📌 Reason: AI assessment failed. "
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

client = Client("http://localhost:9004/")
client.set_credentials(tabpy_user, tabpy_pass)

client.deploy(
    "check_system",
    check_system,
    "AI-based laptop suitability assessment by team (Personal systems only)",
    override=True,
)

print("SUCCESS: AI-based check_system endpoint deployed.")
