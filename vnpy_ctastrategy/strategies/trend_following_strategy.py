import numpy as np
from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    Direction,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class MacdStrategy(CtaTemplate):
    """"""
    author = "EG"

    # entry_window = 20
    # exit_window = 10
    # atr_window = 20
    # fixed_size = 1

    # entry_up = 0
    # entry_down = 0
    # exit_up = 0
    # exit_down = 0
    # atr_value = 0

    # long_entry = 0
    # short_entry = 0
    # long_stop = 0
    # short_stop = 0

    # parameters = ["entry_window", "exit_window", "atr_window", "fixed_size"]
    # variables = ["entry_up", "entry_down", "exit_up", "exit_down", "atr_value"]
    parameters = []
    variables  = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
        self.macds = list()
        self.target_pos = 0

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("Strategy initialized")
        self.load_bar(1)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("Strategy started")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("Strategy stopped")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.cancel_all()

        self.am.update_bar(bar)
        if self.am.count < 26:
            return
        else:
            fast_ema = self.am.ema(12)
            slow_ema = self.am.ema(26)
            macd     = fast_ema - slow_ema
            self.macds.append(macd)

        if not self.am.inited:
            return

        macd /= np.std(self.macds[-20:])
        if self.pos == 0:
            if macd > 1:
                self.target_pos = 1
            elif macd < -1:
                self.target_pos = -1
        elif self.pos > 0:
            if macd < 0:
                self.target_pos = 0
        elif self.pos < 0:
            if macd > 0:
                self.target_pos = 0

        pos_change = self.target_pos - self.pos

        if pos_change > 0:
            self.buy(bar.close_price, pos_change)
        elif pos_change < 0:
            self.short(bar.close_price, -pos_change)

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.write_log(f"trade: {trade}")
        self.write_log(f"pos: {self.pos}")

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        self.write_log(f"order: {order}")
        pass

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass