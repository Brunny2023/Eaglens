# GitHub Actions Deployment Guide for Eaglens

This guide explains how to use the provided GitHub Actions workflow to manage the deployment of your Eaglens Telegram Bot.

## 1. Workflow Overview

The `deploy.yml` workflow is triggered on every push to the `main` branch or manually via `workflow_dispatch`. It performs the following steps:
1.  **Checkout Code**: Retrieves the latest version of the bot code.
2.  **Set up Python**: Configures the environment with Python 3.11.
3.  **Install Dependencies**: Installs all required Python libraries (`python-telegram-bot`, `scikit-learn`, etc.).
4.  **Run Bot (Placeholder)**: This step is a placeholder. GitHub Actions runners are designed for short-lived tasks, not for hosting long-running services like a Telegram bot.

## 2. Recommended Deployment Strategy

For continuous, 24/7 operation, you must use a dedicated hosting service. The GitHub Actions workflow should be modified to *build* and *deploy* to that service, not run the bot directly.

### Recommended Hosting Platforms:
| Platform | Type | Best For | Deployment Method |
| :--- | :--- | :--- | :--- |
| **Render** | PaaS (Platform as a Service) | Easy setup, continuous deployment | Connect GitHub repo, specify start command (`python bot.py`). |
| **Railway** | PaaS | Simple, fast deployment | Connect GitHub repo, automatically detects Python app. |
| **DigitalOcean/AWS** | VPS (Virtual Private Server) | Full control, long-term stability | Use GitHub Actions to SSH into the server and run the bot using a process manager like **PM2** or **Supervisor**. |

## 3. Configuring GitHub Secrets

The bot requires sensitive credentials. You **MUST** configure these as secrets in your GitHub repository settings (`Settings` -> `Secrets and variables` -> `Actions`).

| Secret Name | Value | Purpose |
| :--- | :--- | :--- |
| `TELEGRAM_TOKEN` | `8412034421:AAHsfCrH00KDe7iTKhyFXdmdPkoLA8SoY-g` | Your bot's unique token from @BotFather. |
| `FOOTBALL_DATA_API_KEY` | `b2d4e4fd5ed54f6b967fd6c40f2c6635` | Your API key for fetching football data. |

**Note**: The `config.py` file is set up to read these values from environment variables, which is the secure way to handle secrets in a production environment.

## 4. Finalizing Deployment (VPS Example)

If you choose a VPS, you would modify the `deploy.yml` to include an SSH deployment step:

```yaml
# ... (Steps 1-3 remain the same)

    - name: Deploy to VPS via SSH
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SSH_HOST }}
        username: ${{ secrets.SSH_USERNAME }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /path/to/eaglens_bot
          git pull origin main
          # Restart the bot process using PM2
          pm2 restart eaglens || pm2 start python bot.py --name eaglens
```
This approach ensures the bot is restarted on your server every time you push an update to GitHub.
