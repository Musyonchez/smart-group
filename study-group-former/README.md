# Study Group Former

A Java application for grouping students by course.

## Project Structure

```
study-group-former/
├── build.gradle
├── settings.gradle
├── .gitignore
├── src/
│   ├── main/java/implementation/
│   │   ├── Student.java
│   │   └── StudyGroupFormer.java
│   └── test/java/tests/
│       └── StudyGroupFormerTest.java
```

## Setup & Running

### Option 1: Using Gradle (Recommended)

**Prerequisites:** Java 17+ and Gradle installed

```bash
# Compile
gradle build

# Run tests
gradle test

# View test results
# Output will show in the console
```

### Option 2: Using NetBeans

1. **Open in NetBeans:**
   - File → Open Project
   - Select the `study-group-former` folder
   - NetBeans will automatically recognize it as a Gradle project

2. **Run Tests:**
   - Right-click project → Test Project
   - Or use keyboard shortcut: `Shift + F6`

3. **Build Project:**
   - Right-click project → Build
   - Or use keyboard shortcut: `F11`

### Option 3: Command Line (Java Compiler)

```bash
# Compile main code
mkdir -p build/classes/java/main
javac -d build/classes/java/main src/main/java/implementation/*.java

# Compile tests (requires JUnit on classpath)
# This requires downloading JUnit JAR files
```

## Test Cases

The project includes 5 JUnit 5 tests:

- `shouldGroupStudentsByCourse()` - Verifies students are grouped by course
- `emptyListShouldThrowException()` - Ensures null list throws exception
- `nullListShouldThrowException()` - Ensures empty list throws exception
- `studentsWithSameCourseShouldBeInSameGroup()` - Verifies same course = same group
- `differentCoursesShouldFormDifferentGroups()` - Verifies different courses = different groups

## Java Requirements

- **Java Version:** 17 or higher
- **Testing Framework:** JUnit 5 (Jupiter)
- **Build Tool:** Gradle (optional, can use NetBeans GUI)

## Features

- Groups students by their course
- Validates input (non-null, non-empty lists)
- Throws `IllegalArgumentException` for invalid input
- Lightweight implementation (~40 lines of code)
