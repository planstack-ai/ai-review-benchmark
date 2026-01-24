# frozen_string_literal: true

class ProfilesController < ApplicationController
  def update
    @user = current_user

    if @user.update(profile_params)
      render json: @user
    else
      render json: { errors: @user.errors }, status: :unprocessable_entity
    end
  end

  private

  def profile_params
    params.require(:user).permit(:name, :email)
  end
end
