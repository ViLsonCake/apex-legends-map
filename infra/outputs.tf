output "function_url" {
  description = "Telegram webhook URL"
  value       = aws_lambda_function_url.bot.function_url
}

output "function_name" {
  value = aws_lambda_function.bot.function_name
}
