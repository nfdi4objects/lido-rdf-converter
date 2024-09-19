deps:
	[ -d .venv ] || python3 -m venv .venv
	.venv/bin/pip3 install -r requirement.txt
