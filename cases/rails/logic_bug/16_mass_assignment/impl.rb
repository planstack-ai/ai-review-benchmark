# frozen_string_literal: true

class UsersController < ApplicationController
  def update
    @user = User.find(params[:id])

    # BUG: Mass Assignment 脆弱性
    # params[:user] に role: "admin" を含めると権限昇格できる
    if @user.update(params[:user].permit!)
      render json: @user
    else
      render json: { errors: @user.errors }, status: :unprocessable_entity
    end
  end
end
