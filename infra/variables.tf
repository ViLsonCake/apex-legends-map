variable "region" {
  type    = string
  default = "eu-central-1"
}

variable "project" {
  type    = string
  default = "apex-legends-map-bot"
}

variable "telegram_bot_token" {
  type      = string
  sensitive = true
}

variable "apex_api_key" {
  type      = string
  sensitive = true
}

variable "telegram_webhook_secret" {
  description = "Value Telegram sends in X-Telegram-Bot-Api-Secret-Token (1-256 chars of A-Z, a-z, 0-9, _ and -)"
  type        = string
  sensitive   = true

  validation {
    condition     = can(regex("^[A-Za-z0-9_-]{1,256}$", var.telegram_webhook_secret))
    error_message = "telegram_webhook_secret must be 1-256 characters of A-Z, a-z, 0-9, _ or -."
  }
}

variable "log_retention_days" {
  type    = number
  default = 14
}
