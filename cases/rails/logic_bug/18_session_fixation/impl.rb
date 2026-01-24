# frozen_string_literal: true

class SessionsController < ApplicationController
  def create
    user = User.authenticate(params[:email], params[:password])

    if user
      # BUG: セッション固定攻撃に脆弱
      # reset_session を呼ばずにセッションIDを使い回している
      session[:user_id] = user.id
      redirect_to root_path, notice: "ログインしました"
    else
      flash.now[:alert] = "メールアドレスまたはパスワードが違います"
      render :new
    end
  end
end
