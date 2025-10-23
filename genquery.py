import random

def generate_random_distribution(sessions, total_bytes):
    if not sessions:
        return []

    n = len(sessions)
    weights = [random.random() for _ in range(n)]
    total_weight = sum(weights)
    allocated = [int((w / total_weight) * total_bytes) for w in weights]
    diff = total_bytes - sum(allocated)
    allocated[-1] += diff

    queries = []
    for i, session in enumerate(sessions, start=1):
        lower = max(1, int(allocated[i-1] * 0.05))
        upper = max(lower, int(allocated[i-1] * 0.2))
        acct_input = random.randint(lower, upper)
        acct_output = allocated[i-1] - acct_input
        q = (
            f"-----------------------------------Query {i}-----------------------------------\n\n"
            f"UPDATE radacct\n"
            f"SET acctinputoctets = {acct_input}, acctoutputoctets = {acct_output}\n"
            f"WHERE acctsessionid = '{session}';\n"
            

        )
        queries.append(q)
    return queries

def parse_size_to_bytes(size_str):
    if not isinstance(size_str, str) or not size_str.strip():
        raise ValueError("Invalid size input. Use formats like 2.1GB or 500MB.")
    s = size_str.strip().lower().replace(" ", "")
    try:
        if "gb" in s or s.endswith("g"):
            return int(float(s.replace("gb", "").replace("g", "")) * 1024**3)
        if "mb" in s or s.endswith("m"):
            return int(float(s.replace("mb", "").replace("m", "")) * 1024**2)
        int_part = s.split(".")[0]
        val = float(s)
        if len(int_part) == 1:
            return int(val * 1024**3)
        return int(val * 1024**2)
    except Exception:
        raise ValueError("Invalid size input. Use formats like 2.1GB or 500MB.")
