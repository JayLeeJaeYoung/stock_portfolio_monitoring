# Stock Portfolio Monitoring

A lightweight **Dash web application** for tracking stock portfolios.

## Overview

This app provides a simple way to monitor and manage stock tickers with a clean web interface. Users can log in to:

- **Add, edit, or delete** stock tickers in their watchlist
- **View stock data** in an interactive, sortable table powered by [dash-ag-grid](https://dash.plotly.com/dash-ag-grid)
- **Receive portfolio alerts** on a daily, weekly, and monthly basis via scheduled GitHub Actions

## How it works

- Stock data is retrieved from a third-party API (details redacted in this public release).
- Data is stored in **MongoDB** for persistence.
- Users can manually **refresh or reload** the data to get the latest stock updates, due to free tier API rate limits.
- GitHub Actions run on a cron schedule to generate and send alerts.
- The front-end is built with **Dash** and designed using **dash-mantine-components** for a modern and responsive interface.

## Features

- 🔄 Manual refresh/reload of stock data to respect free tier API limits
- 🔒 User authentication for personalized watchlists
- 📈 Automatic stock data retrieval and storage
- 🗓️ Scheduled alerts (daily, weekly, monthly)
- 📊 Interactive data table using **dash-ag-grid**
- 🎨 Clean, responsive design using **dash-mantine-components**
- 🛠️ Flexible backend powered by MongoDB

## Deployment

A live version of the app is available at [portfolio-dashboard-ldcl.onrender.com](https://portfolio-dashboard-ldcl.onrender.com/).

> ⚠️ **Note on Render free tier:**
>
> - The app may take **up to ~20 seconds** to respond when first visiting the URL, as the free tier spins up the server from sleep.
> - The free tier puts apps into **sleep mode after a period of inactivity**, so subsequent requests may also experience a short delay.
> - This behavior is normal for Render’s free hosting and is not a problem with the app itself.

## Demo Video

Watch a short demo of the app here:

[[Watch the demo]](https://1drv.ms/v/c/e576ffdc03dfe1b2/EQ7v9RmVmtRNv_Q3knpOwSYBsWngAUK4jzTgoqOl4rtAFg?e=u4gooH)

---

_Note: This is a public version with certain code and API details redacted._
