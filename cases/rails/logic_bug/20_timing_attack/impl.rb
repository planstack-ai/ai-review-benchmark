# frozen_string_literal: true

class ApiAuthenticationService
  def initialize(request)
    @request = request
  end

  def authenticate
    provided_token = @request.headers["Authorization"]&.split(" ")&.last
    return nil unless provided_token

    # BUG: タイミング攻撃に脆弱
    # == による比較は一致しない文字が見つかった時点で終了する
    # 比較時間の差から正しいトークンを推測できる
    api_token = ApiToken.find_by(token: provided_token)
    return nil unless api_token&.token == provided_token

    api_token.user
  end
end
