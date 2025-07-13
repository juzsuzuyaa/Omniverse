🌌 The Omniverse RPG - WhatsApp Bot
Welcome to The Omniverse RPG, a powerful and interactive text-based role-playing game system integrated directly with WhatsApp.

This project allows players to experience RPG progression, market interactions, class evolution, and much more — all through simple text commands on WhatsApp, powered by Node.js, Python, and MySQL.

🚀 Features
🎮 Player Registration & Profiles

Players are identified by their WhatsApp number and have stats like HP, energy, strength, techniques, and currencies.

📈 Training System

Upgrade strength, HP, or energy using training coins or evolution items (Rank F / Rank E).

🛒 Technique Market

Players can view, purchase, and upgrade combat techniques.

Techniques require specific requisites (categories).

Each upgrade doubles the attack/resistance and energy cost.

Special costs apply for high-damage techniques (e.g., 1000 training coins above 25,000 power).

🧠 Requirement System

Techniques are associated with "requisites" (e.g., Water Manipulation).

Custom queries allow listing techniques by requisite or which players have them.

🏆 Titles & Achievements

Admins can assign unique titles to players.

Titles are stored and retrievable as a mark of glory and milestones.

🧙 Class Advancement

Players must meet specific requirements in life, energy, strength, and technique levels to evolve into higher classes (E, D, etc.).

⚙️ Tech Stack
Node.js (with puppeteer-whatsapp)

Manages message listening and response through WhatsApp Web.

Python

Executes database logic, rule enforcement, and dynamic responses.

MySQL

Stores player data, techniques, upgrades, logs, titles, and more.

📦 Project Structure
/scripts
  |-- registrar_jogador.py
  |-- aprimorar_forca.py
  |-- tecnicas_por_requisito.py
  |-- associar_titulo_jogador.py
  |-- verificar_subida_classe.py
  |-- ...
/bot.js
/database.sql

🧠 About
This project was created with the goal of gamifying text interactions inside WhatsApp using real RPG progression systems. It supports advanced class evolution, strict requirement validation, and builds a structured database over time — all while maintaining a fun and immersive user experience.

🤝 Contributions
Feel free to fork and expand the system! Pull requests, suggestions, and ideas are welcome.

📧 Contact
If you'd like to talk or collaborate, feel free to reach out!
