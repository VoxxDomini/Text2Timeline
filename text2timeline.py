from backend.commons.t2t_logging import log_info, log_error
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "-cli":
            import cli_runner
            cli_runner.run_cli()
        else:
            print(f"Unrecognized command line argument {sys.argv[1]} passed, exiting.")
    else:
        from backend.flask.app_templated import app
        app.run(debug=True, host="0.0.0.0")
