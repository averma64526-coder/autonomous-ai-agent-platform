# 🤖 Autonomous AI Agent Platform

> An AI-powered autonomous agent platform where users describe a goal, and AI breaks it into tasks, executes them, verifies results, and reports progress — with human-in-the-loop approval for sensitive actions.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [What is this?](#-what-is-this)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Multi-Agent System](#-multi-agent-system)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🎯 What is this?

This platform demonstrates how **autonomous AI agents** can work together to accomplish complex goals. Give it a high-level goal like *"Build a personal portfolio website"* and it will:

1. 🧠 **Decompose** the goal into actionable tasks (AI-powered)
2. ⚡ **Execute** each task with AI reasoning
3. ✅ **Verify** the results with a dedicated AI verifier
4. 🔧 **Recover** from failures using an AI critic
5. 👤 **Request human approval** for sensitive actions
6. 📊 **Stream live activity** logs to a React dashboard

Built as a full-stack portfolio project showcasing modern AI agent architecture.

---

## ✨ Features

### 🧠 Multi-Agent System
- **Planner Agent** — Breaks high-level goals into actionable tasks
- **Executor Agent** — Executes each task with detailed AI reasoning
- **Verifier Agent** — Validates task results with confidence scores
- **Critic Agent** — Recovers from failures by re-planning

### 👤 Human-in-the-Loop
- Sensitive actions require user approval
- Approve/Reject workflow
- Full audit trail of all decisions

### 📊 Real-Time Monitoring
- Live agent activity feed with color-coded logs
- Timestamped execution tracking
- Task status updates (pending → running → completed/failed)

### 🎨 Modern Dashboard
- Beautiful React + Tailwind CSS UI
- Create, decompose, and execute goals visually
- No Swagger/Postman needed for basic usage

### 🔐 Production-Grade Backend
- RESTful API with FastAPI
- SQLAlchemy ORM with 6 relational tables
- Pydantic validation
- Interactive Swagger docs at `/docs`

---

## 🏗️ Architecture