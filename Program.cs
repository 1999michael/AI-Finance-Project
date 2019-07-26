using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;

namespace Quarterly_Reports
{
    class Program
    {
        static String[] scrape(String start, String stop, String text)
        {
            int found = 0;
            int sc = 0;
            String acc = "";
            int stl = start.Length;
            int idx = 0;
            String modified = "0";
            for (int i =0; i<text.Length; i++)
            {
                if(found == 0)
                {
                    found = 1;
                    for (int s = 0; s < start.Length; s++)
                    {
                        if ((i + s) >= text.Length)
                        {
                            break;
                        }
                        if (start[s] != text[i + s])
                        {
                            found = 0;
                        }
                    }
                }
                else if(found == 1)
                {
                    stl--;
                    if (stl == 1)
                    {
                        found = 2;
                    }
                }
                else {
                    sc = 1;
                    for (int s = 0; s < stop.Length; s++)
                    {
                        if ((i + s) >= text.Length)
                        {
                            break;
                        }
                        if (stop[s] != text[i + s])
                        {
                            sc = 0;
                        }
                    }
                    if (sc == 1)
                    {
                        idx = i;
                        break;
                    }
                    acc += text[i];
                    modified = "1";
                }
            }
            String rt = text.Substring(idx + 1);
            return new String[] {acc, rt, modified};
        }

        public static void DownloadFile(string remoteFilename, string localFilename)
        {
            WebClient client = new WebClient();
            client.DownloadFile(remoteFilename, localFilename);
        }

        static void extractQuarter(String sym)
        {

        }


        static void Main(string[] args)
        {
            List<String> symbol = new List<string>();
            String stock_symb = File.ReadAllText(@"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\Stock_Symbols_CSV.json");
            String[] s = new string[] { "", stock_symb, "0" };
            
            for(int itr = 0; itr<309; itr++)
            {
                s = scrape("\":\"", "\"", s[1]);
                symbol.Add(s[0]);
            }

            int enable = 0;
            //downlaod main html files
            foreach (String sym in symbol)
            {
                if(sym == "SWM")
                {
                    enable = 1;
                    
                }


                
                if (enable ==1)
                {
                    Console.WriteLine(sym);
                    DownloadFile("https://www.sec.gov/cgi-bin/browse-edgar?CIK="+sym+"&owner=exclude&action=getcompany", @"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\html\" + sym + ".html");
                    String main_page = File.ReadAllText(@"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\html\" + sym + ".html");
                    String lk = scrape("title=\"ATOM\" href=\"", "amp;count", main_page)[0];
                    int start_id = 0;

                    if(lk == "")
                    {
                        continue;
                    }

                    String total_page = "";
                    String page = "";
                    while (true)
                    {
                        String full_link = "https://www.sec.gov" + lk + "start=" + start_id + "&amp;count=100";
                        DownloadFile(full_link, @"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\html\" + sym + start_id.ToString() + ".html");
                        page = File.ReadAllText(@"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\html\" + sym + start_id.ToString() + ".html");
                        String[] str = scrape("value=\"Next 100\"", "n", page);

                        
                        total_page += page;
                        
                        if (str[2] == "0")
                        {
                            break;
                        }
                        start_id += 100;
                        Console.WriteLine(start_id);
                    }


                    List<String> report = new List<String>();
                    List<String> date = new List<String>();
                    String[] qua = new string[] { "", total_page, "0" };
                    while (true)
                    {
                        qua = scrape(">10-Q</td>", "id=\"interactiveDataBtn", qua[1]);
                        if ((qua[2] == "0") || (qua[0].Length > 400))
                        {
                            break;
                        }

                        if ((qua[0].Length < 400) && (qua[2] == "1"))
                        {
                            report.Add("https://www.sec.gov" + scrape("&nbsp; <a href=\"", "\"", qua[0])[0]);
                        }
                        date.Add(scrape("           <td>", "</td>", qua[1])[0]);
                    }

                    List<String> report2 = new List<String>();
                    List<String> date2 = new List<String>();
                    qua = new string[] { "", total_page, "0" };
                    while (true)
                    {
                        qua = scrape(">10-K</td>", "id=\"interactiveDataBtn", qua[1]);
                        if ((qua[2] == "0") || (qua[0].Length > 400))
                        {
                            break;
                        }

                        if ((qua[0].Length < 400) && (qua[2] == "1"))
                        {
                            report2.Add("https://www.sec.gov" + scrape("&nbsp; <a href=\"", "\"", qua[0])[0]);
                        }
                        date2.Add(scrape("           <td>", "</td>", qua[1])[0] + "[Annual]");
                    }





                    int idx_limit = 0;
                    int year;
                    for (int r = 0; r < date.Count; r++)
                    {
                        String j = date[r].Substring(0, 4);
                        year = System.Convert.ToInt32(j);
                        if (year <= 2015)
                        {
                            idx_limit = r;
                            break;
                        }
                    }
                    report = report.GetRange(0, idx_limit);
                    date = date.GetRange(0, idx_limit);

                    int idx_limit2 = 0;
                    int year2;
                    for (int r = 0; r < date2.Count; r++)
                    {
                        String j = date2[r].Substring(0, 4);
                        year2 = System.Convert.ToInt32(j);
                        if (year2 <= 2015)
                        {
                            idx_limit2 = r;
                            break;
                        }
                    }
                    report2 = report2.GetRange(0, idx_limit2);
                    date2 = date2.GetRange(0, idx_limit2);

                    for (int y = 0; y < report2.Count; y++)
                    {
                        report.Add(report2[y]);
                        date.Add(date2[y]);
                    }



                    string root = @"C:\Users\classic1017\Desktop\Quarterly Reports\" + sym;
                    // If directory does not exist, create it. 
                    if (!Directory.Exists(root))
                    {
                        Directory.CreateDirectory(root);
                    }

                    String pg;
                    for (int g = 0; g < report.Count; g++)
                    {
                        DownloadFile(report[g], @"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\html\" + sym + date[g] + ".html");
                        pg = File.ReadAllText(@"D:\Stock Project\Data Collection\Quarterly Reports\bin\Debug\html\" + sym + date[g] + ".html");

                        String rp = "https://www.sec.gov" + scrape("xbrlviewer\" href=\"", "\"", pg)[0];
                        DownloadFile(rp, root + "\\" + date[g] + ".xlsx");
                    }

                    //break;
                }
                




                //break; //one for now
            }
            

            Console.WriteLine(s[0]);
        }
    }
}
