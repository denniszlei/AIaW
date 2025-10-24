# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commonly Used Commands

- **Install dependencies:** `pnpm i`
- **Start development server:** `quasar dev`
- **Lint files:** `pnpm lint`
- **Build for production (SPA):** `quasar build`
- **Build for production (PWA):** `quasar build -m pwa`

## High-level Code Architecture

This is a cross-platform AI client built with the Quasar framework (Vue.js). It supports various AI providers like OpenAI, Anthropic, and Google.

The application is designed to work on Windows, Linux, Mac OS, Android, and the Web (as a PWA). It uses Capacitor to build for native mobile platforms.

Key features include:
- **Multiple workspaces and assistants:** Allows organizing conversations and assistants.
- **Local-first data storage:** Uses Dexie.js for local data storage with optional cloud synchronization.
- **Plugin system:** Supports custom plugins, including Gradio applications.
- **MCP Protocol:** Implements the Model-Centric Protocol for tools, prompts, and resources.

The application's web directory is `dist/spa`, as configured in `capacitor.config.ts`.