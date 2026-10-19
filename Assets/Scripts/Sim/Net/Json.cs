using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace StarWars.Sim
{
    /// <summary>
    /// Minimaler, abhängigkeitsfreier JSON-Parser/-Writer (Unity-unabhängig, thread-sicher).
    /// Werte: Dictionary&lt;string,object&gt;, List&lt;object&gt;, string, long, double, bool, null.
    /// </summary>
    public static class Json
    {
        public static string Serialize(object value, bool pretty = false)
        {
            var sb = new StringBuilder();
            Write(sb, value, pretty, 0);
            return sb.ToString();
        }

        private static void Indent(StringBuilder sb, bool pretty, int level) { if (pretty) { sb.Append('\n'); sb.Append(' ', level * 2); } }

        private static void Write(StringBuilder sb, object v, bool pretty, int level)
        {
            switch (v)
            {
                case null: sb.Append("null"); break;
                case string s: WriteString(sb, s); break;
                case bool b: sb.Append(b ? "true" : "false"); break;
                case int i: sb.Append(i.ToString(CultureInfo.InvariantCulture)); break;
                case long l: sb.Append(l.ToString(CultureInfo.InvariantCulture)); break;
                case float f: WriteDouble(sb, f); break;
                case double d: WriteDouble(sb, d); break;
                case IDictionary<string, object> dict:
                    sb.Append('{'); bool first = true;
                    foreach (var kv in dict)
                    {
                        if (!first) sb.Append(','); first = false;
                        Indent(sb, pretty, level + 1); WriteString(sb, kv.Key); sb.Append(pretty ? ": " : ":"); Write(sb, kv.Value, pretty, level + 1);
                    }
                    if (!first) Indent(sb, pretty, level);
                    sb.Append('}'); break;
                case System.Collections.IEnumerable list:
                    sb.Append('['); bool f2 = true;
                    foreach (var item in list)
                    {
                        if (!f2) sb.Append(','); f2 = false;
                        Indent(sb, pretty, level + 1); Write(sb, item, pretty, level + 1);
                    }
                    if (!f2) Indent(sb, pretty, level);
                    sb.Append(']'); break;
                default: WriteString(sb, Convert.ToString(v, CultureInfo.InvariantCulture)); break;
            }
        }

        private static void WriteDouble(StringBuilder sb, double d)
        {
            if (double.IsNaN(d) || double.IsInfinity(d)) { sb.Append("0"); return; }
            string s = d.ToString("R", CultureInfo.InvariantCulture);
            sb.Append(s);
            if (s.IndexOf('.') < 0 && s.IndexOf('E') < 0 && s.IndexOf('e') < 0) sb.Append(".0");
        }

        private static void WriteString(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4")); else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
        }

        // ------------------------------------------------------------------ Parser
        public static object Parse(string text)
        {
            if (text == null) throw new FormatException("JSON ist null");
            int pos = 0;
            var v = ParseValue(text, ref pos, 0);
            SkipWs(text, ref pos);
            if (pos != text.Length) throw new FormatException("Unerwartete Zeichen nach JSON-Wert");
            return v;
        }

        public static bool TryParse(string text, out object value)
        {
            try { value = Parse(text); return true; } catch (Exception) { value = null; return false; }
        }

        private static void SkipWs(string s, ref int p) { while (p < s.Length && (s[p] == ' ' || s[p] == '\n' || s[p] == '\r' || s[p] == '\t' || s[p] == '\uFEFF')) p++; }

        private static object ParseValue(string s, ref int p, int depth)
        {
            if (depth > 64) throw new FormatException("JSON zu tief verschachtelt");
            SkipWs(s, ref p);
            if (p >= s.Length) throw new FormatException("Unerwartetes Ende");
            char c = s[p];
            if (c == '{')
            {
                p++; var d = new Dictionary<string, object>();
                SkipWs(s, ref p);
                if (p < s.Length && s[p] == '}') { p++; return d; }
                while (true)
                {
                    SkipWs(s, ref p);
                    if (p >= s.Length || s[p] != '"') throw new FormatException("Schlüssel erwartet");
                    string key = ParseString(s, ref p);
                    SkipWs(s, ref p);
                    if (p >= s.Length || s[p] != ':') throw new FormatException("':' erwartet");
                    p++;
                    d[key] = ParseValue(s, ref p, depth + 1);
                    SkipWs(s, ref p);
                    if (p >= s.Length) throw new FormatException("Unerwartetes Ende");
                    if (s[p] == ',') { p++; continue; }
                    if (s[p] == '}') { p++; return d; }
                    throw new FormatException("',' oder '}' erwartet");
                }
            }
            if (c == '[')
            {
                p++; var l = new List<object>();
                SkipWs(s, ref p);
                if (p < s.Length && s[p] == ']') { p++; return l; }
                while (true)
                {
                    l.Add(ParseValue(s, ref p, depth + 1));
                    SkipWs(s, ref p);
                    if (p >= s.Length) throw new FormatException("Unerwartetes Ende");
                    if (s[p] == ',') { p++; continue; }
                    if (s[p] == ']') { p++; return l; }
                    throw new FormatException("',' oder ']' erwartet");
                }
            }
            if (c == '"') return ParseString(s, ref p);
            if (Match(s, p, "true")) { p += 4; return true; }
            if (Match(s, p, "false")) { p += 5; return false; }
            if (Match(s, p, "null")) { p += 4; return null; }
            return ParseNumber(s, ref p);
        }

        private static bool Match(string s, int p, string lit) => string.CompareOrdinal(s, p, lit, 0, lit.Length) == 0;

        private static object ParseNumber(string s, ref int p)
        {
            int start = p; bool isFloat = false;
            if (p < s.Length && (s[p] == '-' || s[p] == '+')) p++;
            while (p < s.Length)
            {
                char c = s[p];
                if (c >= '0' && c <= '9') p++;
                else if (c == '.' || c == 'e' || c == 'E' || c == '-' || c == '+') { isFloat = true; p++; }
                else break;
            }
            if (p == start) throw new FormatException("Ungültiges JSON-Zeichen '" + s[p] + "'");
            string num = s.Substring(start, p - start);
            if (!isFloat && long.TryParse(num, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out long l)) return l;
            if (double.TryParse(num, NumberStyles.Float, CultureInfo.InvariantCulture, out double d)) return d;
            throw new FormatException("Ungültige Zahl: " + num);
        }

        private static string ParseString(string s, ref int p)
        {
            p++; var sb = new StringBuilder();
            while (true)
            {
                if (p >= s.Length) throw new FormatException("String nicht beendet");
                char c = s[p++];
                if (c == '"') return sb.ToString();
                if (c != '\\') { sb.Append(c); continue; }
                if (p >= s.Length) throw new FormatException("Ungültige Escape-Sequenz");
                char e = s[p++];
                switch (e)
                {
                    case '"': sb.Append('"'); break;
                    case '\\': sb.Append('\\'); break;
                    case '/': sb.Append('/'); break;
                    case 'b': sb.Append('\b'); break;
                    case 'f': sb.Append('\f'); break;
                    case 'n': sb.Append('\n'); break;
                    case 'r': sb.Append('\r'); break;
                    case 't': sb.Append('\t'); break;
                    case 'u':
                        if (p + 4 > s.Length) throw new FormatException("Ungültiges \\u");
                        sb.Append((char)Convert.ToInt32(s.Substring(p, 4), 16)); p += 4; break;
                    default: throw new FormatException("Ungültige Escape-Sequenz");
                }
            }
        }

        // ------------------------------------------------------------------ Hilfsfunktionen (Python: _safe_int / _safe_float ...)
        public static string Str(IDictionary<string, object> d, string key, string def = "")
            => d != null && d.TryGetValue(key, out var v) && v != null ? Convert.ToString(v, CultureInfo.InvariantCulture) : def;

        public static long Int(IDictionary<string, object> d, string key, long def = 0, long min = long.MinValue, long max = long.MaxValue)
        {
            long r = def;
            if (d != null && d.TryGetValue(key, out var v) && v != null)
            {
                if (v is long l) r = l;
                else if (v is double db && !double.IsNaN(db) && !double.IsInfinity(db)) r = (long)db;
                else if (v is bool b) r = b ? 1 : 0;
                else if (v is string s && long.TryParse(s, NumberStyles.Integer, CultureInfo.InvariantCulture, out var ps)) r = ps;
            }
            return Math.Max(min, Math.Min(max, r));
        }

        public static double Num(IDictionary<string, object> d, string key, double def = 0, double min = -1e7, double max = 1e7)
        {
            double r = def;
            if (d != null && d.TryGetValue(key, out var v) && v != null)
            {
                if (v is double db) r = db; else if (v is long l) r = l;
                else if (v is string s && double.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out var ps)) r = ps;
            }
            if (double.IsNaN(r) || double.IsInfinity(r)) r = def;
            return Math.Max(min, Math.Min(max, r));
        }

        public static bool Bool(IDictionary<string, object> d, string key, bool def = false)
            => d != null && d.TryGetValue(key, out var v) && v is bool b ? b : def;

        public static Dictionary<string, object> Obj(IDictionary<string, object> d, string key)
            => d != null && d.TryGetValue(key, out var v) ? v as Dictionary<string, object> : null;

        public static List<object> Arr(IDictionary<string, object> d, string key)
            => d != null && d.TryGetValue(key, out var v) ? v as List<object> : null;
    }
}
