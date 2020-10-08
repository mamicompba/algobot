from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from credentials import telegramApi
from datetime import datetime


class TelegramBot:
    def __init__(self, gui):
        self.updater = Updater(telegramApi, use_context=True)

        # Get the dispatcher to register handlers
        self.gui = gui
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("help", self.help_telegram))
        dp.add_handler(CommandHandler("override", self.override_telegram))
        dp.add_handler(CommandHandler(('stats', 'statistics'), self.get_statistics_telegram))
        dp.add_handler(CommandHandler("forcelong", self.force_long_telegram))
        dp.add_handler(CommandHandler("forceshort", self.force_short_telegram))
        dp.add_handler(CommandHandler('exitposition', self.exit_position_telegram))
        dp.add_handler(CommandHandler(("position", 'getposition'), self.get_position_telegram))
        dp.add_handler(CommandHandler(('fuckpeter', 'ispetergay', 'fuckyoupeter'), self.peter))
        dp.add_handler(CommandHandler(('ismihirgay', 'fuckmihir', 'fuckyoumihir'), self.mihir))
        dp.add_handler(CommandHandler(('praisemihir', 'mihirisalegend', 'phonkboi'), self.mihir1))

    def start(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

    def stop(self):
        self.updater.stop()

    @staticmethod
    def help_telegram(update, context):
        update.message.reply_text("Here are your help commands available:\n"
                                  "/help -> To get commands available.\n"
                                  "/forcelong  -> To force long.\n"
                                  "/forceshort -> To force short.\n"
                                  "/position or /getposition -> To get position.\n"
                                  "/stats or /statistics -> To get current statistics.\n"
                                  "/override -> To exit trade and wait for next cross.\n"
                                  "/exitposition -> To exit position.")

    def get_statistics_telegram(self, update, context):
        startingBalance = self.gui.trader.startingBalance
        profit = self.gui.trader.get_profit()
        position = self.gui.trader.get_position()
        coinName = self.gui.trader.coinName
        if position == -1:
            pos = 'Short'
        elif position == 1:
            pos = 'Long'
        else:
            pos = None
        if profit >= 0:
            label = 'Profit'
        else:
            label = 'Loss'
        runtime = datetime.utcnow() - self.gui.trader.startingTime
        update.message.reply_text(f"Here are your statistics:\n"
                                  f'Symbol: {self.gui.trader.symbol}\n'
                                  f'Position: {pos}\n'
                                  f"Coin owned: {self.gui.trader.coin}\n"
                                  f"Coin owed: {self.gui.trader.coinOwed}\n"
                                  f"Starting balance: ${round(startingBalance, 2)}\n"
                                  f"Balance: ${round(self.gui.trader.balance, 2)}\n"
                                  f"{label}: ${round(abs(profit), 2)}\n"
                                  f'{label} Percentage: {round(abs(profit / startingBalance), 2)}%\n'
                                  f'Autonomous Mode: {self.gui.trader.inHumanControl}\n'
                                  f'Stop Loss: ${round(self.gui.trader.get_stop_loss(), 2)}\n'
                                  f'Run time: {runtime}\n'
                                  f"Current {coinName} price: ${self.gui.trader.dataView.get_current_price()}"
                                  )

    def override_telegram(self, update, context):
        update.message.reply_text("Overriding.")
        self.gui.exit_position(False)
        update.message.reply_text("Successfully overrode.")

    def force_long_telegram(self, update, context):
        position = self.gui.trader.get_position()
        if position == 1:
            update.message.reply_text("Bot is already in a long position.")
        else:
            update.message.reply_text("Forcing long.")
            self.gui.force_long()
            update.message.reply_text("Successfully forced long.")

    def force_short_telegram(self, update, context):
        position = self.gui.trader.get_position()
        if position == -1:
            update.message.reply_text("Bot is already in a short position.")
        else:
            update.message.reply_text("Forcing short.")
            self.gui.force_short()
            update.message.reply_text("Successfully forced short.")

    def exit_position_telegram(self, update, context):
        if self.gui.trader.get_position() == 0:
            update.message.reply_text("Bot is not in a position.")
        else:
            update.message.reply_text("Exiting position.")
            self.gui.exit_position(True)
            update.message.reply_text("Successfully exited position.")

    def get_position_telegram(self, update, context):
        position = self.gui.trader.get_position()
        if position == -1:
            update.message.reply_text("Bot is currently in a short position.")
        elif position == 1:
            update.message.reply_text("Bot is currently in a long position.")
        else:
            update.message.reply_text("Bot is currently not in any position.")

    @staticmethod
    def peter(update, context):
        update.message.reply_text("Yes, you are right because Peter is an australian wanker kangaroo cunt.")

    @staticmethod
    def mihir(update, context):
        update.message.reply_text('No, do not say those things. Mihir is a legend.')

    @staticmethod
    def mihir1(update, context):
        update.message.reply_text("Praise be mihir. PHONKBOIZ UNITED")

