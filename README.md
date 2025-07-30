# Matched Betting Bot

## Overview

This Discord-integrated matched betting bot helps users find high-value betting opportunities (called **conversions**) and perform quick profitability calculations. It automates the process of identifying profitable bets using back and lay odds, while also supporting currency conversion between AUD and NZD.

---

## What is a Conversion?

A **conversion** in matched betting represents the expected retained value (as a percentage) from a bonus bet after placing a corresponding lay bet. There are two main types:

- **SNR (Stake Not Returned)**: Used for bonus bets where the stake isn't returned in winnings.
- **SR (Stake Returned)**: Used for standard bets where the stake is returned upon winning.

Higher conversion percentages indicate more profitable matched betting opportunities.

---

## Key Features

### 🔎 Find Top Conversions
- Use `/get_snr` and `/get_sr` to retrieve the top 6 matched betting opportunities.
- Filter by:
  - Bookmaker
  - Minimum liquidity (in AUD)
  - Maximum lay odds
  - Event cutoff date

### 🧮 Built-in Calculators
- `/calculate_snr` and `/calculate_sr`: Compute lay stake, liability, and profit based on:
  - Stake amount
  - Back and lay odds
  - Betfair commission
  - Currency (AUD/NZD)
- `/calculate_snr_liquidity` and `/calculate_sr_liquidity`: Determine the maximum stake allowed given a liquidity limit.

### 🌐 Currency Support
- Converts between AUD and NZD in all relevant calculations.
- Exchange rates are updated automatically every 12 hours via a public currency API.

### 📘 Help Command
- `/conversions_help`: Lists available bookmakers and how to use conversion commands effectively.

---

## Supported Bookmakers

- sportsbet  
- tab / tabnz  
- bet365  
- ladbrokes  
- unibet  
- bluebet  
- topsport  
- betright  
- betr  
- neds  
- betdeluxe  
- palmerbet  
- picklebet  
- pointsbet  
- realbookie  
- elitebet  
- crossbet  
- tab touch  

---

## Configuration

Create a `config.json` file with the following structure:

```json
{
  "username": "your_email@example.com",
  "password": "your_password",
  "currencyAPI": "your_currency_api_key",
  "discordBotToken": "your_discord_bot_token"
}

---

## Running the Bot

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Start the bot
python bot.py

---

## Disclaimer

This bot is intended for informational and educational purposes only. Use of matched betting tools and strategies may violate the terms and conditions of some bookmakers. Use responsibly and at your own discretion.
