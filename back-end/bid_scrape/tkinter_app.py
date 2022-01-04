import json
import tkinter as tk
from tkinter import ttk
from scrapy.signalmanager import dispatcher
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapyscript import Job, Processor

END_PAGE = "End page"

START_PAGE = "Start page"

LINK = "Link"

CATEGORY_INFORMATION = "Category information"

CRAWL = "CRAWL"

HOME = "Home"

CRAWL_RANGE_OF_PAGES = "Crawl range of pages"

BIDDING_SCRAPY_CRAWLER = "Bidding scrapy crawler"

CRAWL_SPECIFIC_PAGE = "Crawl specific page"

LARGE_FONT = ("Verdana", 25)
MEDIUM_FONT = ("Verdana", 10)

OPTION = {"contractor_bidding_correction": "Thông báo gia hạn / đính chính",
          "contractor_bidding_invitation": "Thông báo mời thầu",
          "contractor_bidding_result": "Kết quả trúng thầu",
          "contractor_information": "Thông tin nhà thầu",
          "contractor_online_bidding_result": "Kế hoạch mở thầu điện tử",
          # pre qualification result for contractor
          "contractor_selection_plan": "Kế hoạch lựa chọn nhà thầu",
          "contractor_short_listing": "Danh sách ngắn"}


class tkinterApp(tk.Tk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, Page1, Page2):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# first window frame startpage

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # label of frame Layout 2
        label = ttk.Label(self, text=BIDDING_SCRAPY_CRAWLER, font=LARGE_FONT)

        # putting the grid in its place by using
        # grid
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text=CRAWL_SPECIFIC_PAGE,
                             command=lambda: controller.show_frame(Page1))

        # putting the button in its place by
        # using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        # button to show frame 2 with text layout2
        button2 = ttk.Button(self, text=CRAWL_RANGE_OF_PAGES,
                             command=lambda: controller.show_frame(Page2))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)


# second window frame page1
class Page1(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text=CRAWL_SPECIFIC_PAGE, font=LARGE_FONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(self, text=HOME,
                             command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button2 = ttk.Button(self, text=CRAWL_RANGE_OF_PAGES,
                             command=lambda: controller.show_frame(Page2))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)

        option_label = ttk.Label(self, text=CATEGORY_INFORMATION, font=MEDIUM_FONT)
        option_label.grid(row=1, column=4)
        n = tk.StringVar()
        option = ttk.Combobox(self, textvariable=n, width=30, state="readonly")
        option["values"] = tuple(OPTION.values())
        option.grid(row=2, column=4)
        option.current(1)

        link_label = ttk.Label(self, text=LINK, font=MEDIUM_FONT)
        link_label.grid(row=3, column=4)
        link_var = tk.StringVar()
        link_entry = ttk.Entry(self, textvariable=link_var, width=30)
        link_entry.grid(row=4, column=4)

        submit_btn = ttk.Button(self, text=CRAWL,
                                command=lambda: self.crawl(link_var=link_var, combobox_selected=option.get()))
        submit_btn.grid(row=5, column=4, padx=10, pady=10)

    def crawl(self, link_var, combobox_selected):
        link = link_var.get()
        spider_name = list(OPTION.keys())[list(OPTION.values()).index(combobox_selected)]
        settings = get_project_settings()
        process = CrawlerProcess(settings=settings)
        process.crawl(spider_name, single_link=link)
        process.start()


# third window frame page2
class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text=CRAWL_RANGE_OF_PAGES, font=LARGE_FONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(self, text=CRAWL_SPECIFIC_PAGE,
                             command=lambda: controller.show_frame(Page1))

        # putting the button in its place by
        # using grid
        button1.grid(row=1, column=1, padx=10, pady=10)

        # button to show frame 3 with text
        # layout3
        button2 = ttk.Button(self, text=HOME,
                             command=lambda: controller.show_frame(StartPage))

        # putting the button in its place by
        # using grid
        button2.grid(row=2, column=1, padx=10, pady=10)

        option_label = ttk.Label(self, text=CATEGORY_INFORMATION, font=MEDIUM_FONT)
        option_label.grid(row=1, column=4)
        n = tk.StringVar()
        option = ttk.Combobox(self, textvariable=n, width=30, state="readonly")
        option["values"] = tuple(OPTION.values())
        option.grid(row=2, column=4)
        option.current(1)

        start_page_label = ttk.Label(self, text=START_PAGE)
        start_page_label.grid(row=3, column=4)
        start_page_var = tk.IntVar()
        start_page_entry = ttk.Entry(self, textvariable=start_page_var, width=30)
        start_page_entry.grid(row=4, column=4)

        end_page_label = ttk.Label(self, text=END_PAGE)
        end_page_label.grid(row=5, column=4)
        end_page_var = tk.IntVar()
        end_page_entry = ttk.Entry(self, textvariable=end_page_var, width=30)
        end_page_entry.grid(row=6, column=4)

        submit_btn = ttk.Button(self, text=CRAWL,
                                command=lambda: self.crawl(start_page_var=start_page_var,
                                                           end_page_var=end_page_var,
                                                           combobox_selected=option.get()))
        submit_btn.grid(row=7, column=4, padx=10, pady=10)

    def crawl(self, start_page_var, end_page_var, combobox_selected):
        print(f"Button clicked from {start_page_var} to {end_page_var} and selected {combobox_selected}")
        settings = get_project_settings()
        spider_name = list(OPTION.keys())[list(OPTION.values()).index(combobox_selected)]
        process = CrawlerProcess(settings=settings)
        process.crawl(spider_name, start_page=start_page_var.get(), end_page=end_page_var.get())
        process.start()

# Driver Code
app = tkinterApp()
app.mainloop()

