#include <iostream>
#include <string>
#include <stdexcept>
#include <cmath>

using namespace std;

const int screenWidth = 800;
const int screenHeight = 600;

class Point2d
{
private: 
	int x;
	int y;

public:
	Point2d() : x(0), y(0) {}

	Point2d(int x, int y, int screenWidth, int screenHeight)
	{
		if (x < 0 || y < 0 || x >= screenWidth || y >= screenHeight)
		{
			throw invalid_argument("Координаты должны быть внутри окна (начало координат левый нижний угол)");
		}

		this->x = x;
		this->y = y;
	}

	int getX() const { return x; }

	int getY() const { return y; }

	string pointToString()const
	{
		return "point(x=" + to_string(x) + ", y=" + to_string(y) + ")";
	}
};


class Vector2d
{
private:
	Point2d head;
	Point2d end;
	int x;
	int y;

public:
	Vector2d() : x(0), y(0) {};

	Vector2d(Point2d headPoint, Point2d endPoint)
	{
		x = headPoint.getX() - endPoint.getX();
		y = headPoint.getY() - endPoint.getY();
	}

	Vector2d(int x, int y)
	{

		if (x <= 0 || y <= 0 || x >= screenWidth || y >= screenHeight)
		{
			throw invalid_argument("Координаты должны быть внутри окна (начало координат левый нижний угол)");
		}
		
		this->x = x;
		this->y = y;
		
	}

	void setCoordX(int coordX) { x = coordX; }
	void setCoordY(int coordY) { y = coordY; }
	
	int getCoordX() { return x; }
	int getCoordY() { return y; }

	double lenght() const 
	{
		return sqrt(pow(2, x) + pow(2, y));
	}
	
	int dotProduct(Vector2d& other) const
	{
		return x * other.x + y * other.y;
	}

	int crossProduct(Vector2d& other) const
	{
		return x * other.y - other.x * y;
	}

	int mixedProduct(Vector2d& firVec, Vector2d& secVec, Vector2d& thirVec) const
	{
		//voprosiki
		return 0;
	}

	Vector2d operator+(const Vector2d& other) const
	{
		return Vector2d(x + other.x, y + other.y);
	}

	Vector2d operator-(const Vector2d& other) const
	{
		return Vector2d(x - other.x, y - other.y);
	}

	string vectorToString() const
	{
		return "vector(x= "+ to_string(x) + ", y= " + to_string(y) + ")";
	}
	
	Vector2d operator*(int k) const
	{
		return Vector2d(x * k, y * k);
	}
};

int main()
{
	setlocale(LC_ALL, "Russian");

	try{
		Point2d point(300, 200, screenWidth, screenHeight);
		cout << point.pointToString() << endl;
		Vector2d coordsVector(50, 50);
		cout << coordsVector.vectorToString() << endl;
	}
	catch (const invalid_argument& e) {
		cerr << e.what() << endl;
	}

	Point2d headPoint(200, 300, screenWidth, screenHeight);
	Point2d endPoint(15, 50, screenWidth, screenHeight);

	Vector2d pointVector(headPoint, endPoint);
	Vector2d secCoordsVector(8, 10);
	
	cout << "Вектор по двум точкам: " << pointVector.vectorToString() << endl;
	cout << "Длинна вектора по двум точкам: " << pointVector.lenght() << endl;
	cout << "Вектор по координатам: " << secCoordsVector.vectorToString() << endl;
	cout << "Длинна вектора по координатам: " << secCoordsVector.lenght() << endl;
	
	pointVector.setCoordX(100); 
	secCoordsVector.setCoordY(30);

	cout << "Координата x вектора по двум точкам: " << pointVector.getCoordX() << endl;
	cout << "Координата y вектора по координатам: " << secCoordsVector.getCoordY() << endl;
	
	cout << "Скалярное произведение: " << pointVector.dotProduct(secCoordsVector) << endl;
	cout << "Векторное произведение: " << secCoordsVector.crossProduct(pointVector) << endl;
	
	Vector2d summ = secCoordsVector + pointVector;
	Vector2d remainder = pointVector - secCoordsVector;
	
	cout << "Вектор суммы: " << summ.vectorToString() << endl;
	cout << "Вектор разности: " << remainder.vectorToString() << endl;

}
