"""
Computes XML metadata part feature extraction which is used by the RSC_main_test_v5 file for testing
"""


class metadata_xml:
    c = 0
    d = 0
    e = 0

    def journal_code(self, mydoc):
        """
        Extracts the journal code from the XML metadata
        :param mydoc: parsed XML
        :return: level based on the journal code
        """
        j_code = mydoc.getElementsByTagName('shortCode')
        for elem in j_code:
            # print(elem.firstChild.data)
            j_code = elem.firstChild.data
            j_code = j_code.upper()
            if ((j_code == 'EW') | (j_code == 'CY')):
                self.c = 1
            elif ((j_code == 'CE') | (j_code == 'RE') | (j_code == 'EN')):
                self.c = 2
            elif ((j_code == 'LC') | (j_code == 'ME') | (j_code == 'MD')):
                self.c = 3
            else:
                print("journal code", j_code)
                self.c = 2
        # print("c--->", self.c)
        return self.c

    def article_title(self, mydoc):
        a_title = mydoc.getElementsByTagName('workingTitle')
        for elem in a_title:
            return (elem.firstChild.data)

    def authors_nation(self, mydoc):
        """
                Extracts the authors_nation from the XML metadata
                :param mydoc: parsed XML
                :return: level based on the authors_nation
        """
        asian_countries = ["AFGHANISTAN", "ARMENIA", "AZERBAIJAN", "BAHRAIN", "BANGLADESH", "BHUTAN", "BRUNEI",
                           "CAMBODIA", "CHINA",
                           "CYPRUS", "GEORGIA", "INDIA", "INDONESIA", "IRAN", "IRAQ", "ISRAEL", "JAPAN", "JORDAN",
                           "KAZAKHSTAN", "KUWAIT", "KYRGYZSTAN", "LAOS",
                           "LEBANON", "MALAYSIA", "MALDIVES", "MONGOLIA", "MYANMAR", "BURMA", "NEPAL", "NORTH KOREA",
                           "NORTHKOREA", "OMAN", "PAKISTAN", "PALESTINE", "PHILIPPINES",
                           "QATAR", "RUSSIA", "SAUDI ARABIA", "SAUDIARABIA", "SINGAPORE", "SOUTH KOREA", "SOUTHKOREA",
                           "SRI LANKA", "SRILANKA", "SYRIA", "TAIWAN", "TAJIKISTAN", "THAILAND",
                           "TIMOR - LESTE", "TIMOR-LESTE", "TIMOR LESTE", "TIMORLESTE", "TURKEY", "TURKMENISTAN",
                           "UNITED ARAB", "UNITEDARAB", "EMIRATES(UAE)", "UZBEKISTAN", "VIETNAM", "YEMEN"]

        authors = mydoc.getElementsByTagName('author')
        for elem in authors:
            if (elem.attributes['role'].value == "corresponding"):
                corr_author_nation = elem.getElementsByTagName('country')
                for elem1 in corr_author_nation:
                    print(elem1.firstChild.data)
                    country = elem1.firstChild.data
                    country = country.upper()
                    if ((country == 'US') | (country == 'UK') | (country == 'CANADA') | (country == 'CN') | (country == 'AUSTRALIA') | (country == 'AU') | (country == 'UNITED STATES') | (country == 'UNITED KINGDOM') | (country == 'UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND')):
                        self.d = 1
                    elif ((country == 'JPN') | (country == 'JAPAN') | (country == 'EUROPE') | (country == 'EUROPE UNION') | (country == 'EU') | (country == 'KOREA') | (country == 'SINGAPORE')):
                        self.d = 2
                    elif ((country == 'CH') | (country == 'CHINA') | (country == 'INDIA2') | (country == 'MIDDLE EAST') | (country == 'RUSSIAN FEDERATION') | (country == 'RUSSIA') | (country == 'TURKEY') | (country == 'TAIWAN')):
                        self.d = 3
                    elif (country in asian_countries):
                        self.d = 3
                    else:
                        print("authors_nation", country)
                        self.d = 2
                print("d--->", self.d)

                return self.d

    def type_article(self, mydoc):
        """
                Extracts the type_articlefrom the XML metadata
                :param mydoc: parsed XML
                :return: level based on the type_article
        """

        t_article = mydoc.getElementsByTagName('typeCode')
        for elem in t_article:
            # print(elem.firstChild.data)
            type_arc = elem.firstChild.data
            type_arc = type_arc.upper()
            if ((type_arc == 'COM') | (type_arc == 'COMMENT')):
                self.e = 1
            elif ((type_arc == 'ART') | (type_arc == 'RES') | (type_arc == 'RESEARCH')):
                self.e = 2
            elif ((type_arc == 'PER') | (type_arc == 'REV') | (type_arc == 'HIGHLIGHT') | (type_arc == 'HIG') | (type_arc == 'REVIEW')):
                self.e = 3
            else:
                print("type_article", type_arc)
                self.e = 2
        # print("e--->", self.e)
        return self.e

# import glob2
# path="D:\\PycharmProjects\\CE_RSC_client\\sample files for CE\\*\\*\\*.docx"
# files = glob2.glob(path)
# for file in files:
#     x = metadata_xml()
#     # file='D:\PycharmProjects\CE_RSC_client\sample files for CE\DIFFICULT\C8CE01099D\C8CE01099D_orig.docx__preprocessed.docx'
#     tmp_doc_file_path = file
#     pos = tmp_doc_file_path.rfind('\\')
#     # print(pos)
#     # print(tmp_doc_file_path[pos + 1])
#     xml_file_path = tmp_doc_file_path[0:(pos + 11)] + "_metadata.xml"
#     # print(xml_file_path)
#
#     # if (pos != -1):
#     #     doc_file_path = tmp_doc_file_path[0:pos]
#     #     print(doc_file_path)
#     #     xml_file_path = doc_file_path + "_metadata.xml"
#     # else:
#     #     xml_file_path = tmp_doc_file_path.replace("__preprocessed", "_metadata.xml", 1)
#
#     # print(xml_file_path)
#     mydoc = minidom.parse(xml_file_path)
#
#     d = x.journal_code(mydoc)
#     e = x.authors_nation(mydoc)
#     f = x.type_article(mydoc)
    # print(" Score based on metadata extraction for ", file, d, e, f)

    # OTHER ASAIN COUNTRIES
    # Afghanistan, Armenia, Azerbaijan, Bahrain, Bangladesh, Bhutan, Brunei, Burma, Cambodia, China, East
    # Timor, Georgia, Hong
    # Kong, India, Indonesia, Iran, Iraq, Israel, Japan, Jordan, Kazakhstan, Kuwait, Kyrgyzstan, Laos, Lebanon, Malaysia, Mongolia, Nepal, North
    # Korea, Oman, Pakistan, Papua
    # New
    # Guinea, Philippines, Qatar, Russia, Saudi
    # Arabia, Singapore, South
    # Korea, Sri
    # Lanka, Syria, Taiwan, Tajikistan, Thailand, Turkey, Turkmenistan, United
    # Arab
    # Emirates, Uzbekistan, Vietnam, Yemen.

    # EU COUNTRIES
    # France
    # Germany
    # Italy
    # Luxembourg
    # Netherlands
    # Denmark
    # Ireland
    # United
    # Kingdom
    # Greece
    # Portugal
    # Spain
    # Austria
    # Finland
    # Sweden
    # Cyprus
    # Czech
    # Republic
    # Estonia
    # Hungary
    # Latvia
    # Lithuania
    # Malta
    # Poland
    # Slovakia
    # Slovenia
    # Bulgaria
    # Romania
    # Croatia
