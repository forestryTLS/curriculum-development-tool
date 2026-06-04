### AI Suggestions Feature End-to-End Tests

These are end-to-end browser tests don't run automatically with `composer test`.

Like the other tests, make sure the database is initialized and the server is running on your device before running the tests. Instructions are in `docs/Setup.md`, under *Database Setup*.

Then complete the following set up specific to these tests:

##### Browser Playwrights
Install the browser playwrights with `npx playwright install` from the `laravel/` directory. This will install mock browsers onto your system, using around 0.5GB of storage. You can remove these after running the tests with `npx playwright uninstall`, and reinstall them later if necessary.

<small>
Optional: If you'd like these to install onto a specific drive, follow <a href="https://playwright.dev/docs/browsers#managing-browser-binaries">these configuration steps</a>. However, as of writing this, only the default set up has been tested.
</small>

##### Docker
Ensure you have docker on your device, with enough space to create a container. The LocalStack container takes around 1GB of system storage. The actual container creation (and deletion) are handled by the script.

##### Running the LocalStack server

##### Running the tests 

Then run these tests specifically with `composer test:ai-suggestions-e2e`.

*Debugging*

To see the browser as the tests run, use `composer test:ai-suggestions-e2e:debug`.
If you want to be able to step, set the env variable 
- Linux, Mac, WSL: `export PW_DEBUG="1"`
- Windows: `$PW_DEBUG="1"`.

Setting it back to `"0"` disables stepping.


##### Notes

Since LocalStack doesn't currently support SageMaker, we've 'mocked' quite a few tasks in the tests by sending requests to test endpoints.

`MainWorkflowTest.php` has a lot of comments to explain what's going on. The other tests follow a similar logic.
