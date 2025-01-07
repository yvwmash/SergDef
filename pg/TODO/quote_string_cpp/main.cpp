#include <iostream>
#include <xlnt/xlnt.hpp>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libgen.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <grp.h>

std::string quote(const std::string& src){
 std::string out;

 for(const char& c : src){
  out.push_back(c);
  if(c == '"'){
   out.push_back(c);
  }
 }

 return out;
}

int main(int argc, char *argv[])
{
 std::string s = " \"abc\"\" ";

 std::cout << s << std::endl;
 std::cout << quote(s) << std::endl;
 return 0;
}