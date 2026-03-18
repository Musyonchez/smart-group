package implementation;

import java.util.List;

public class Student {
    private String name;
    private String course;
    private String strength;
    private String weakness;
    private List<String> availability;

    public Student(String name, String course, String strength, String weakness, List<String> availability) {
        this.name = name;
        this.course = course;
        this.strength = strength;
        this.weakness = weakness;
        this.availability = availability;
    }

    public String getName() {
        return name;
    }

    public String getCourse() {
        return course;
    }

    public String getStrength() {
        return strength;
    }

    public String getWeakness() {
        return weakness;
    }

    public List<String> getAvailability() {
        return availability;
    }
}
