from sqlmodel import select, desc, update , delete
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from auth.services import AuthService
from uuid import UUID
from db.models import User, Order, Review, Product
from user.schemas import UserUpdate


auth_services= AuthService()

class UserService:
    async def get_all_users(self, session :AsyncSession):
        try:
            statement = select(User).where(User.is_active==True).order_by(desc(User.created_at))
            result = await session.exec(statement)
            users= result.all()
            return users

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"FAILED TO FETCH USERS: {str(e)}")

    async def get_user(self,user_id:UUID, session:AsyncSession):
        try:
            statement= select(User).where(User.user_id == user_id)
            result = await session.exec(statement)
            user= result.first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"USER NOT FOUND")
            return user

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch user")

    async def update_user(self, user_id:UUID, update_data:UserUpdate,  session:AsyncSession):
        try:
            user_to_update= await self.get_user(user_id, session)
            if not user_to_update:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,detail="USER NOT FOUND"
                )
            update_data_dict =update_data.model_dump(exclude_unset=True)

            if "email" in update_data_dict:
                existing_user = await auth_services.get_user_by_email(update_data_dict["email"], session)
                if existing_user and existing_user.user_id != user_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

            if user_to_update.deleted_at and update_data_dict.get("is_active", True):
                update_data_dict["deleted_at"] = None

            for key, value in update_data_dict.items():
                setattr(user_to_update, key, value)
            await session.commit()
            await session.refresh(user_to_update)
            return user_to_update
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")

    async def delete_user(self,username,user_id, session:AsyncSession):
        try:
            user = await auth_services.get_user_by_username(username, session)
            if not user:
                raise HTTPException(
                    status_code=404, detail="USER NOT FOUND")
            statement= select(Order).where(Order.user_id==user_id)
            result = await session.exec(statement)
            orders = result.all()
            for order in orders:
                order.user_id = None
            await session.commit()
            await session.delete(user)
            await session.commit()
            return {"message": "User deleted successfully"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

