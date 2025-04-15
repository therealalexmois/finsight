"""Юнит-тесты для DTO с краткой информацией о счетах Tinkoff."""

from typing import TYPE_CHECKING

import pytest

from src.finsight_api.infrastructure.dto.tinkoff.account_summary_dto import AccountSummaryDTO

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from pytest_mock import MockFixture
    from tinkoff.invest import Account


@pytest.mark.unit
class TestAccountSummaryDTO:
    @staticmethod
    @pytest.mark.parametrize(
        'account_ids',
        [
            ['acc1', 'acc2', 'acc3'],
            ['only'],
            [],
            [None, 123, 'valid'],
        ],
    )
    def test_from_sdk__should_create_dto_from_sdk_data(
        mocker: 'MockFixture',
        account_ids: 'Sequence[Any]',
    ) -> None:
        """Should correctly create DTO from SDK data."""
        sdk_accounts: Sequence[Account] = [mocker.Mock(id=acc_id) for acc_id in account_ids]

        dto = AccountSummaryDTO.from_sdk(sdk_accounts)

        assert dto.accounts_count == len(account_ids)
        assert dto.account_ids == account_ids

    @staticmethod
    @pytest.mark.parametrize(
        'accounts_count, account_ids',
        [
            (0, []),
            (2, ['a1', 'a2']),
            (3, ['x', 'y', 'z']),
        ],
    )
    def test_to_model__should_convert_dto_to_domain_model(
        accounts_count: int,
        account_ids: 'Sequence[str]',
    ) -> None:
        """Should convert DTO to domain model."""
        dto = AccountSummaryDTO(accounts_count=accounts_count, account_ids=account_ids)

        model = dto.to_model()

        assert model.accounts_count == accounts_count
        assert model.account_ids == account_ids
