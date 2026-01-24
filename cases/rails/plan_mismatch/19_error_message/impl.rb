# frozen_string_literal: true

class ErrorResponseService
  HTTP_STATUS_MAP = {
    "E001" => 400,
    "E002" => 404,
    "E003" => 401,
    "E004" => 403,
    "E500" => 500
  }.freeze

  def invalid_params_response
    # BUG: ハードコードされた数値 1 を使用
    # ErrorCode::INVALID_PARAMS（"E001"）を使うべき
    build_response(1, "パラメータが不正です", 400)
  end

  def not_found_response
    # BUG: 同様にハードコードされた数値
    build_response(2, "リソースが見つかりません", 404)
  end

  private

  def build_response(code, message, status)
    {
      error: {
        code: code,
        message: message
      },
      status: status
    }
  end
end
