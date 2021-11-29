class XpathConstants:
    GET_TEXT = "text()"
    GET_ALL_CHILDREN_TEXT = "//text()"
    GET_A_TAG = "/a"
    XPATH_GET_NGAY_PHE_DUYET = "//h4[text() = 'Ngày phê duyệt']/following-sibling::h3/text()"
    XPATH_GET_NGAY_DANG_TAI = "//h4[text() = 'Ngày đăng tải']/following-sibling::h3/text()"
    XPATH_GET_THOI_DIEM_DANG_TAI = "//h4[text() = 'Thời điểm đăng tải']/following-sibling::h3/text()"
    XPATH_GET_THOI_DIEM_DONG_THAU = "//h4[text() = 'Thời điểm đóng thầu']/following-sibling::h3/text()"
    XPATH_GET_TR_TAG_THONG_TIN_CHI_TIET = "//span[text() = 'THÔNG TIN CHI " \
                                          "TIẾT']/../following-sibling::div/div/div/table/tr"
    XPATH_GET_TR_TAG_THAM_DU_THAU = "//span[text() = 'Tham dự thầu']/../following-sibling::div/div/div/table/tr"
    XPATH_GET_TR_TAG_MOI_THAU = "//span[text() = 'MỜI THẦU']/../following-sibling::div/div/div/table/tr"
    XPATH_GET_TR_TAG_BAO_DAM_DU_THAU = "//span[text() = 'BẢO ĐẢM DỰ THẦU']/../following-sibling::div/div/div/table/tr"
    XPATH_GET_HINH_THUC_THAU = "//div[@class = 'bg-l2']/h3/text()"
    XPATH_GET_LINKS = "//a[@class = 'container-tittle']/@href"


class DocumentConstants:
    THONG_TIN_CHI_TIET_UPPER_CASE = "THÔNG TIN CHI TIẾT"
    THONG_TIN_CHI_TIET = "Thông tin chi tiết"
    NGAY_DANG_TAI = "Ngày đăng tải"
    NGAY_PHE_DUYET = "Ngày phê duyệt"
    HINH_THUC_DAU_THAU = "Hình thức đấu thầu"
    TEN_NHA_THAU = "Tên nhà thầu"
    LINH_VUC = "Lĩnh vực"
    KET_QUA_UPPER_CASE = "KẾT QUẢ"
    KET_QUA = "Kết quả"
    GIA_GOI_THAU = "Giá gói thầu"
    MO_TA_TOM_TAT_GOI_THAU_UPPER_CASE = "MÔ TẢ TÓM TẮT GÓI THẦU"
    MO_TA_TOM_TAT_GOI_THAU = "Mô tả tóm tắt gói thầu"
    CAC_NHA_THAU_TRUNG_THAU_KHAC = "Các nhà thầu trúng thầu khác"
    CAC_NHA_THAU_TRUNG_THAU_KHAC_UPPER_CASE = "CÁC NHÀ THẦU TRÚNG THẦU KHÁC"
    NHA_THAU_TRUNG_THAU = "Nhà thầu trúng thầu"
    GOI_THAU_DA_THAM_GIA = "Gói thầu đã tham gia"
    SO_HIEU_KHLCNT = "Số hiệu KHLCNT"
    TEN_GOI_THAU = "Tên gói thầu"
    BEN_MOI_THAU = "Bên mời thầu"
    GIA_TRUNG_THAU = "Giá trúng thầu"
    DONG_TRUNG_THAU = "Đồng trúng thầu"
    TRUNG_THAU = "Trúng thầu"
    TEN_HANG_HOA = "Tên hàng hóa"
    SO_LUONG = "Số lượng"
    XUAT_XU = "Xuất xứ"
    GIA_DON_GIA_TRUNG_THAU = "Giá/Đơn giá trúng thầu"
    THAM_DU_THAU = "Tham dự thầu"
    THONG_TIN_CHUNG = "Thông tin chung"
    THONG_TIN_NGANH_NGHE = "Thông tin ngành nghề"
    TEN_DU_AN_DU_TOAN_MUA_SAM = "Tên dự án/ Dự toán mua sắm"
    MO_THAU = "Mở thầu"
    MO_THAU_UPPER_CASE = "MỞ THẦU"
    TEN_TAI_LIEU = "Tên tài liệu"
    LINK = "Link"
    BAO_DAM_DU_THAU = "Bảo đảm dự thầu"
    BAO_DAM_DU_THAU_UPPER_CASE = "BẢO ĐẢM DỰ THẦU"
    HO_SO_MOI_THAU = "Hồ sơ mời thầu"
    LAM_RO_E_HSMT = "Làm rõ E-HSMT"
    THONG_BAO_LIEN_QUAN = "Thông báo liên quan"
    THOI_DIEM_DANG_TAI = "Thời điểm đăng tải"
    THOI_DIEM_DONG_THAU = "Thời điểm đóng thầu"
    SO_TBMT = "Số TBMT"
    GIA_DU_THAU = "Giá dự thầu (VND)"
    GIA_DU_THAU_SAU_GIAM_GIA = "Giá dự thầu sau giảm giá (VND)"
    MOI_THAU = "Mời thầu"


class CollectionConstants:
    CONTRACTOR_HISTORY = "contractorHistory"


class JavaScriptConstants:
    JS_VOID = "javascript:void(0);"

