#include <random>
#include <ctime>
#include <iostream>
#include <functional>
#include <fstream>

using namespace std;

int main()
{
    mt19937 engine((unsigned int)time(NULL));                    // MT19937 난수 엔진
    uniform_int_distribution<int> distribution(0, 256);       // 생성 범위
    auto generator = bind(distribution, engine);

    std::ofstream writeFile;
    writeFile.open("randon.txt");

    // 0~100 범위의 난수 50개 생성하여 출력
    for (int i = 0; i < 50; ++i)
        writeFile << generator() << " ";
}