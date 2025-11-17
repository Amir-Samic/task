#include <iostream>
#include <string>
#include <stack>

bool simpleJsonCheck(const std::string& json) {
    std::stack<char> brackets;
    bool inString = false;
    bool escape = false;
    
    for (size_t i = 0; i < json.length(); i++) {
        char c = json[i];
        
        if (escape) {
            escape = false;
            continue;
        }
        
        if (c == '\\') {
            escape = true;
            continue;
        }
        
        if (c == '"') {
            inString = !inString;
            continue;
        }
        
        if (inString) continue;
        
        if (c == '{' || c == '[') {
            brackets.push(c);
        } else if (c == '}') {
            if (brackets.empty() || brackets.top() != '{') return false;
            brackets.pop();
        } else if (c == ']') {
            if (brackets.empty() || brackets.top() != '[') return false;
            brackets.pop();
        }
    }
    
    return brackets.empty() && !inString;
}

int main() {
    std::string test_json = "{\"name\": \"John\", \"numbers\": [1, 2, 3]}";
    
    if (simpleJsonCheck(test_json)) {
        std::cout << "JSON is valid!" << std::endl;
    } else {
        std::cout << "JSON is invalid!" << std::endl;
    }
    
    return 0;
}
