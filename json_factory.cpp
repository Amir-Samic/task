#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <sstream>

class JsonValue {
public:
    virtual ~JsonValue() = default;
    virtual std::string toString() const = 0;
    virtual std::string serialize(int indent = 0) const = 0;
};

class JsonNull : public JsonValue {
public:
    std::string toString() const override { return "null"; }
    std::string serialize(int indent = 0) const override { return "null"; }
};

class JsonBool : public JsonValue {
private:
    bool value;
public:
    JsonBool(bool v) : value(v) {}
    std::string toString() const override { return value ? "true" : "false"; }
    std::string serialize(int indent = 0) const override { return value ? "true" : "false"; }
    bool getValue() const { return value; }
};

class JsonNumber : public JsonValue {
private:
    double value;
public:
    JsonNumber(double v) : value(v) {}
    std::string toString() const override { return std::to_string(value); }
    std::string serialize(int indent = 0) const override { 
        std::stringstream ss;
        ss << value;
        return ss.str();
    }
    double getValue() const { return value; }
};

class JsonString : public JsonValue {
private:
    std::string value;
public:
    JsonString(const std::string& v) : value(v) {}
    std::string toString() const override { return "\"" + value + "\""; }
    std::string serialize(int indent = 0) const override { 
        return "\"" + escapeString(value) + "\""; 
    }
    std::string getValue() const { return value; }
    
private:
    std::string escapeString(const std::string& str) const {
        std::string result;
        for (char c : str) {
            switch (c) {
                case '"': result += "\\\""; break;
                case '\\': result += "\\\\"; break;
                case '\b': result += "\\b"; break;
                case '\f': result += "\\f"; break;
                case '\n': result += "\\n"; break;
                case '\r': result += "\\r"; break;
                case '\t': result += "\\t"; break;
                default: result += c; break;
            }
        }
        return result;
    }
};

class JsonArray : public JsonValue {
private:
    std::vector<std::shared_ptr<JsonValue>> values;
public:
    void add(std::shared_ptr<JsonValue> value) {
        values.push_back(value);
    }
    
    std::string toString() const override {
        std::string result = "[";
        for (size_t i = 0; i < values.size(); i++) {
            if (i > 0) result += ", ";
            result += values[i]->toString();
        }
        result += "]";
        return result;
    }
    
    std::string serialize(int indent = 0) const override {
        if (values.empty()) return "[]";
        
        std::string spaces(indent, ' ');
        std::string result = "[\n";
        
        for (size_t i = 0; i < values.size(); i++) {
            result += spaces + "  " + values[i]->serialize(indent + 2);
            if (i < values.size() - 1) result += ",";
            result += "\n";
        }
        
        result += spaces + "]";
        return result;
    }
    
    size_t size() const { return values.size(); }
    std::shared_ptr<JsonValue> get(size_t index) const { 
        return index < values.size() ? values[index] : nullptr; 
    }
};

class JsonObject : public JsonValue {
private:
    std::map<std::string, std::shared_ptr<JsonValue>> properties;
public:
    void set(const std::string& key, std::shared_ptr<JsonValue> value) {
        properties[key] = value;
    }
    
    std::string toString() const override {
        std::string result = "{";
        bool first = true;
        for (const auto& [key, value] : properties) {
            if (!first) result += ", ";
            result += "\"" + key + "\": " + value->toString();
first = false;
        }
        result += "}";
        return result;
    }
    
    std::string serialize(int indent = 0) const override {
        if (properties.empty()) return "{}";
        
        std::string spaces(indent, ' ');
        std::string result = "{\n";
        
        bool first = true;
        for (const auto& [key, value] : properties) {
            if (!first) result += ",\n";
            result += spaces + "  \"" + key + "\": " + value->serialize(indent + 2);
            first = false;
        }
        
        result += "\n" + spaces + "}";
        return result;
    }
    
    bool has(const std::string& key) const {
        return properties.find(key) != properties.end();
    }
    
    std::shared_ptr<JsonValue> get(const std::string& key) const {
        auto it = properties.find(key);
        return it != properties.end() ? it->second : nullptr;
    }
};

class JsonFactory {
public:
    static std::shared_ptr<JsonNull> createNull() {
        return std::make_shared<JsonNull>();
    }
    
    static std::shared_ptr<JsonBool> createBool(bool value) {
        return std::make_shared<JsonBool>(value);
    }
    
    static std::shared_ptr<JsonNumber> createNumber(double value) {
        return std::make_shared<JsonNumber>(value);
    }
    
    static std::shared_ptr<JsonNumber> createNumber(int value) {
        return std::make_shared<JsonNumber>(static_cast<double>(value));
    }
    
    static std::shared_ptr<JsonString> createString(const std::string& value) {
        return std::make_shared<JsonString>(value);
    }
    
    static std::shared_ptr<JsonArray> createArray() {
        return std::make_shared<JsonArray>();
    }
    
    static std::shared_ptr<JsonObject> createObject() {
        return std::make_shared<JsonObject>();
    }
    
    // Создание сложных объектов через фабричные методы
    static std::shared_ptr<JsonObject> createUser(const std::string& name, int age, bool isActive) {
        auto user = createObject();
        user->set("name", createString(name));
        user->set("age", createNumber(age));
        user->set("isActive", createBool(isActive));
        return user;
    }
    
    static std::shared_ptr<JsonObject> createProduct(const std::string& title, double price, 
                                                    const std::vector<std::string>& tags) {
        auto product = createObject();
        product->set("title", createString(title));
        product->set("price", createNumber(price));
        
        auto tagsArray = createArray();
        for (const auto& tag : tags) {
            tagsArray->add(createString(tag));
        }
        product->set("tags", tagsArray);
        
        return product;
    }
    
    static std::shared_ptr<JsonArray> createUserList() {
        return createArray();
    }
};


// Демонстрация использования
int main() {
    // Создание простых значений
    auto nullValue = JsonFactory::createNull();
    auto boolValue = JsonFactory::createBool(true);
    auto numberValue = JsonFactory::createNumber(42.5);
    auto stringValue = JsonFactory::createString("Hello, World!");
    
    std::cout << "Простые значения:" << std::endl;
    std::cout << "Null: " << nullValue->serialize() << std::endl;
    std::cout << "Bool: " << boolValue->serialize() << std::endl;
    std::cout << "Number: " << numberValue->serialize() << std::endl;
    std::cout << "String: " << stringValue->serialize() << std::endl;
    std::cout << std::endl;
    
    // Создание массива
    auto array = JsonFactory::createArray();
    array->add(JsonFactory::createNumber(1));
    array->add(JsonFactory::createString("test"));
    array->add(JsonFactory::createBool(false));
    
    std::cout << "Массив:" << std::endl;
    std::cout << array->serialize(2) << std::endl;
std::cout << std::endl;
    
    // Создание объекта
    auto object = JsonFactory::createObject();
    object->set("name", JsonFactory::createString("John"));
    object->set("age", JsonFactory::createNumber(30));
    object->set("scores", array);
    
    std::cout << "Объект:" << std::endl;
    std::cout << object->serialize(2) << std::endl;
    std::cout << std::endl;
    
    // Использование фабричных методов для создания сложных объектов
    auto user = JsonFactory::createUser("Alice", 25, true);
    std::cout << "Пользователь:" << std::endl;
    std::cout << user->serialize(2) << std::endl;
    std::cout << std::endl;
    
    auto product = JsonFactory::createProduct("Laptop", 999.99, {"electronics", "computers", "sale"});
    std::cout << "Продукт:" << std::endl;
    std::cout << product->serialize(2) << std::endl;
    std::cout << std::endl;
    
    // Создание списка пользователей
    auto userList = JsonFactory::createUserList();
    userList->add(JsonFactory::createUser("Bob", 28, true));
    userList->add(JsonFactory::createUser("Charlie", 35, false));
    userList->add(JsonFactory::createUser("Diana", 22, true));
    
    auto usersObject = JsonFactory::createObject();
    usersObject->set("users", userList);
    usersObject->set("total", JsonFactory::createNumber(3));
    
    std::cout << "Список пользователей:" << std::endl;
    std::cout << usersObject->serialize(2) << std::endl;
    
    return 0;
}
