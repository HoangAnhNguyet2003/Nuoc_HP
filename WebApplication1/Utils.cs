using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Web;

namespace WebApplication1
{
    public static class Utils
    {
        public static string connectionString = ConfigurationManager.AppSettings["DB"].ToString();
    }
}