package implementation;

import java.util.*;

public class StudyGroupFormer {

    public List<List<Student>> formGroups(List<Student> students) {
        if (students == null || students.isEmpty()) {
            throw new IllegalArgumentException("Student list cannot be empty");
        }

        Map<String, List<Student>> courseGroups = new HashMap<>();

        // Group by course
        for (Student s : students) {
            courseGroups.putIfAbsent(s.getCourse(), new ArrayList<>());
            courseGroups.get(s.getCourse()).add(s);
        }

        // Convert to list of groups
        return new ArrayList<>(courseGroups.values());
    }
}
