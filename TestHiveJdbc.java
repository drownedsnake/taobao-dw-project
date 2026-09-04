import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class TestHiveJdbc {
    public static void main(String[] args) throws Exception {
        String host = args.length > 0 ? args[0] : "localhost";
        String url = "jdbc:hive2://" + host + ":10000/";
        System.out.println("尝试连接: " + url);
        Connection conn = DriverManager.getConnection(url, "drownedsnake", "");
        System.out.println("连接成功!");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SHOW DATABASES");
        while (rs.next()) {
            System.out.println("database: " + rs.getString(1));
        }
        rs.close();
        stmt.close();
        conn.close();
    }
}
