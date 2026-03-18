package tests;

import implementation.*;
import org.junit.jupiter.api.Test;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class StudyGroupFormerTest {

    @Test
    void shouldGroupStudentsByCourse() {
        StudyGroupFormer former = new StudyGroupFormer();

        List<Student> students = List.of(
            new Student("Perez", "AI", "Math", "Coding", List.of("Mon")),
            new Student("John", "AI", "Coding", "Math", List.of("Mon")),
            new Student("Jane", "Cybersecurity", "Networking", "Crypto", List.of("Tue"))
        );

        List<List<Student>> groups = former.formGroups(students);

        assertEquals(2, groups.size()); // AI + Cybersecurity
    }

    @Test
    void emptyListShouldThrowException() {
        StudyGroupFormer former = new StudyGroupFormer();

        assertThrows(IllegalArgumentException.class, () -> {
            former.formGroups(new ArrayList<>());
        });
    }

    @Test
    void nullListShouldThrowException() {
        StudyGroupFormer former = new StudyGroupFormer();

        assertThrows(IllegalArgumentException.class, () -> {
            former.formGroups(null);
        });
    }

    @Test
    void studentsWithSameCourseShouldBeInSameGroup() {
        StudyGroupFormer former = new StudyGroupFormer();

        List<Student> students = List.of(
            new Student("A", "ML", "Math", "Stats", List.of("Mon")),
            new Student("B", "ML", "Coding", "Math", List.of("Tue"))
        );

        List<List<Student>> groups = former.formGroups(students);

        assertEquals(1, groups.size());
        assertEquals(2, groups.get(0).size());
    }

    @Test
    void differentCoursesShouldFormDifferentGroups() {
        StudyGroupFormer former = new StudyGroupFormer();

        List<Student> students = List.of(
            new Student("A", "AI", "Math", "Stats", List.of("Mon")),
            new Student("B", "Cybersecurity", "Networking", "Crypto", List.of("Tue"))
        );

        List<List<Student>> groups = former.formGroups(students);

        assertEquals(2, groups.size());
    }
}
