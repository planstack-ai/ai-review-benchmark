# frozen_string_literal: true

class SessionsController < ApplicationController
  def create
    user = User.authenticate(params[:email], params[:password])

    if user
      reset_session
      session[:user_id] = user.id
      redirect_to session.delete(:return_to) || root_path
    else
      flash.now[:alert] = "認証に失敗しました"
      render :new
    end
  end
end
