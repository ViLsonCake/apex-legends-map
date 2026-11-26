data "archive_file" "bot" {
  type        = "zip"
  source_dir  = "${path.module}/../src/bot"
  output_path = "${path.module}/build/bot.zip"
  excludes    = ["__pycache__", "**/__pycache__/**"]
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.project}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_cloudwatch_log_group" "bot" {
  name              = "/aws/lambda/${var.project}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "bot" {
  function_name    = var.project
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  architectures    = ["arm64"]
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.bot.output_path
  source_code_hash = data.archive_file.bot.output_base64sha256
  memory_size      = 128
  timeout          = 10

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN      = var.telegram_bot_token
      APEX_API_KEY            = var.apex_api_key
      TELEGRAM_WEBHOOK_SECRET = var.telegram_webhook_secret
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.bot,
    aws_iam_role_policy_attachment.lambda_logs,
  ]
}

resource "aws_lambda_function_url" "bot" {
  function_name      = aws_lambda_function.bot.function_name
  authorization_type = "NONE"
}

# Public Function URLs need both permissions.
resource "aws_lambda_permission" "url_invoke_url" {
  statement_id           = "AllowPublicFunctionUrl"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.bot.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "url_invoke_function" {
  statement_id  = "AllowPublicInvokeViaUrl"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.bot.function_name
  principal     = "*"
}
