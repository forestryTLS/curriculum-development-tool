### AI Suggestions Feature End-to-End Tests

These tests don't run automatically with `composer test`.

To run these, first make sure the browser playwrights are installed with `npx playwright install`. This will install mock browsers onto your system and may take some space. You can remove these after running the tests, and reinstall them later if necessary.

Then run these tests specifically with `composer test:ai-suggestions-e2e`.
