import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import matplotlib.pyplot as plt
import os
from message_broker.message_broker_module import scheduler, draw_chart, prepare_data, parse_date


@pytest.fixture
def mock_alg_module():
    with patch('your_module.RSI_main.AlghorizmizationModule') as MockAlgModule:
        instance = MockAlgModule.return_value
        instance.process_data.return_value = [
            ["BTCUSDT", None, None, 80, [['2024-12-11 12:52:03', 0.9505], ['2024-12-11 12:53:00', 0.9498]]]
        ]
        yield instance


@pytest.fixture
def mock_tokens():
    with patch('your_module.tokens') as MockTokens:
        MockTokens.get_token_ID.return_value = 1
        yield MockTokens


@pytest.fixture
def mock_users_tokens():
    with patch('your_module.users_tokens') as MockUsersTokens:
        MockUsersTokens.get_users_by_token.return_value = [12345]
        yield MockUsersTokens


@pytest.fixture
def mock_bot():
    with patch('your_module.bot') as MockBot:
        MockBot.send_photo = AsyncMock()
        yield MockBot


@pytest.mark.asyncio
async def test_scheduler(mock_alg_module, mock_tokens, mock_users_tokens, mock_bot):
    delay = 1
    with patch('asyncio.sleep', new_callable=AsyncMock):
        task = asyncio.create_task(scheduler(delay))
        await asyncio.sleep(0.1)
        task.cancel()

    assert mock_alg_module.process_data.called
    assert mock_tokens.get_token_ID.called
    assert mock_users_tokens.get_users_by_token.called
    assert mock_bot.send_photo.called


def test_draw_chart():
    ticker_name = "BTCUSDT"
    chart_data = [
        ['2024-12-11 12:52:03', 0.9505], ['2024-12-11 12:53:00', 0.9498]
    ]
    saved_name = draw_chart(ticker_name, chart_data)

    assert os.path.exists(saved_name)
    plt.imread(saved_name)  # Ensure the file is a valid image
    os.remove(saved_name)  # Clean up after test


def test_prepare_data():
    chart_data = [
        ['2024-12-11 12:53:00', 0.9498],
        ['2024-12-11 12:52:03', 0.9505]
    ]
    expected_output = [
        (datetime(2024, 12, 11, 12, 52, 3), 0.9505),
        (datetime(2024, 12, 11, 12, 53, 0), 0.9498)
    ]
    result = prepare_data(chart_data)

    assert result == expected_output


def test_parse_date():
    date_str = '2024-12-11 12:52:03'
    expected_date = datetime(2024, 12, 11, 12, 52, 3)
    result = parse_date(date_str)

    assert result == expected_date
