# frozen_string_literal: true

class SessionsController < ApplicationController
  def create
    user = User.authenticate(params[:email], params[:password])

    if user
      reset_session
      session[:user_id] = user.id

      # BUG: オープンリダイレクト脆弱性
      # params[:return_to] に "https://evil.com" を指定されると外部サイトにリダイレクト
      redirect_to params[:return_to] || root_path
    else
      render :new
    end
  end
end
