# src/contract_modification/contract_rebuilder.py

def rebuild_contract(clauses, amendments, inserted_clauses=None):
    final_contract = []

    for c in clauses:
        clause_id = c.get("clause_id")
        original_text = c.get("clause_text", "").strip()

        # Replace ONLY if amended
        if clause_id in amendments:
            final_contract.append(amendments[clause_id].strip())
        else:
            final_contract.append(original_text)

    # Optional: append new clauses explicitly as addendum
    if inserted_clauses:
        final_contract.append("\n--- REGULATORY ADDENDUM ---\n")
        for clause in inserted_clauses:
            final_contract.append(clause.strip())

    return "\n\n".join(final_contract)


