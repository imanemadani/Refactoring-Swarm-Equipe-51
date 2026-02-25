The Refactoring Swarm
This project was developed for the IGL Lab (2025–2026) at the National School of Computer Science.
The objective is to build an autonomous multi-agent system capable of refactoring poorly written Python code without human intervention.

Project Idea
The system takes as input a folder containing badly structured, buggy, or undocumented Python code.
It analyzes the code, improves it, and validates the result using automated tests.
The goal is not just to fix code, but to design an intelligent architecture that can manage software maintenance automatically.

Architecture
The system is based on three main agents:

Auditor
Analyzes the code and generates a refactoring plan using static analysis.

Fixer
Applies the modifications file by file according to the plan.

Judge
Runs unit tests.
If tests fail, the errors are sent back to the Fixer (self-healing loop).
If tests pass, the process stops.

Features
Automated code analysis
Iterative refactoring loop
Test-based validation using pytest
Static quality improvement using pylint
Experiment logging in JSON format

Technologies
Python
OpenRouter API (LLM models)
Pytest
Pylint
