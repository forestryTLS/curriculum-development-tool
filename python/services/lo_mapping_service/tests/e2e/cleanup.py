"""
Standalone cleanup for E2E test data in Postgres.

Run after a mid-test crash to wipe the high-ID rows the seeded_course_program
fixture would normally tear down. LocalStack/DynamoDB/S3 cleanup is not needed
because those go away with the LocalStack container.

Usage:
    python tests/e2e/cleanup.py

Honours E2E_PG_DSN env var (default: postgresql://root@localhost:5432/laravel).
"""
import os
import sys

import psycopg2

PG_DSN = os.environ.get("E2E_PG_DSN", "postgresql://root@localhost:5432/laravel")

CLEANUP_STATEMENTS = [
    "DELETE FROM outcome_map_ai_suggestions WHERE l_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM outcome_maps                WHERE l_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM course_programs             WHERE course_id = 99001 AND program_id = 99001",
    "DELETE FROM mapping_scale_programs      WHERE program_id = 99001",
    "DELETE FROM program_learning_outcomes   WHERE pl_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM learning_outcomes           WHERE l_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM mapping_scales              WHERE map_scale_id BETWEEN 99001 AND 99002",
    "DELETE FROM programs                    WHERE program_id = 99001",
    "DELETE FROM courses                     WHERE course_id = 99001",
]


def main() -> int:
    print(f"Connecting to {PG_DSN} ...")
    try:
        conn = psycopg2.connect(PG_DSN)
    except Exception as e:
        print(f"FAILED to connect: {e}", file=sys.stderr)
        return 1

    conn.autocommit = False
    cur  = conn.cursor()
    total = 0
    try:
        for sql in CLEANUP_STATEMENTS:
            cur.execute(sql)
            print(f"  {sql.split()[1]:<3} {sql.split()[3]:<35} -> {cur.rowcount} row(s) deleted")
            total += cur.rowcount
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"FAILED, rolled back: {e}", file=sys.stderr)
        return 1
    finally:
        cur.close()
        conn.close()

    print(f"\nDone. {total} row(s) deleted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
