"""
Standalone cleanup for E2E test state after a mid-test crash

Postgres: wipes the high-ID rows the seeded_course_program fixture would have created

Docker: with --docker, force-removes any testcontainers-labelled LocalStack container 
left behind by a crashed pytest session

Usage:
    python tests/e2e/cleanup.py
    python tests/e2e/cleanup.py --docker

Honours E2E_PG_DSN env var (default: postgresql://root@localhost:5432/laravel).
"""
import argparse
import os
import subprocess
import sys

import psycopg2

PG_DSN = os.environ.get("E2E_PG_DSN", "postgresql://root@localhost:5432/laravel")

CLEANUP_STATEMENTS = [
    "DELETE FROM outcome_map_ai_suggestions WHERE l_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM outcome_maps                WHERE l_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM course_users                WHERE course_id = 99001",
    "DELETE FROM program_users               WHERE program_id = 99001",
    "DELETE FROM course_programs             WHERE course_id = 99001 AND program_id = 99001",
    "DELETE FROM mapping_scale_programs      WHERE program_id = 99001",
    "DELETE FROM program_learning_outcomes   WHERE pl_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM learning_outcomes           WHERE l_outcome_id BETWEEN 99001 AND 99002",
    "DELETE FROM mapping_scales              WHERE map_scale_id BETWEEN 99001 AND 99002",
    "DELETE FROM programs                    WHERE program_id = 99001",
    "DELETE FROM courses                     WHERE course_id = 99001",
]


def cleanup_postgres() -> int:
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


def cleanup_docker() -> int:
    """Force-remove testcontainers-labelled LocalStack containers from crashed runs."""
    print("\nLooking for leftover testcontainers LocalStack containers ...")
    try:
        result = subprocess.run(
            [
                "docker", "ps", "-aq",
                "--filter", "label=org.testcontainers=true",
                "--filter", "ancestor=localstack/localstack:3.0",
            ],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        print("  docker CLI not found; skipping.", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"  docker ps failed: {e.stderr.strip()}", file=sys.stderr)
        return 1

    ids = [cid for cid in result.stdout.split() if cid]
    if not ids:
        print("  None found.")
        return 0

    print(f"  Removing {len(ids)} container(s): {' '.join(ids)}")
    try:
        subprocess.run(["docker", "rm", "-f", *ids], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"  docker rm failed: {e.stderr.strip()}", file=sys.stderr)
        return 1
    print("  Done.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", action="store_true", help="also force-remove leftover LocalStack containers")
    args = parser.parse_args()

    rc = cleanup_postgres()
    if args.docker:
        rc = cleanup_docker() or rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
