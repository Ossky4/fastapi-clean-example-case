from unittest.mock import AsyncMock, Mock

import pytest

from app.core.commands.create_user import CreateUser, CreateUserRequest, UserRoleRequestEnum
from app.core.commands.exceptions import UsernameAlreadyExistsError
from tests.unit.core.common.services.factories import create_super_user, create_user


@pytest.mark.asyncio
async def test_propagates_username_already_exists_from_flusher() -> None:
    current_user_service = Mock()
    current_user_service.get_current_user = AsyncMock(return_value=create_super_user())

    created_user = create_user()
    user_service = Mock()
    user_service.create_user_with_raw_password = AsyncMock(return_value=created_user)

    utc_timer = Mock()
    utc_timer.now = created_user.created_at

    user_tx_storage = Mock()

    flusher = Mock()
    flusher.flush = AsyncMock(side_effect=UsernameAlreadyExistsError)

    transaction_manager = Mock()
    transaction_manager.commit = AsyncMock()

    sut = CreateUser(
        current_user_service=current_user_service,
        user_service=user_service,
        utc_timer=utc_timer,
        user_tx_storage=user_tx_storage,
        flusher=flusher,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(UsernameAlreadyExistsError):
        await sut.execute(
            CreateUserRequest(
                username="new-user",
                password="test-password-123",
                role=UserRoleRequestEnum.USER,
            )
        )

    transaction_manager.commit.assert_not_awaited()
